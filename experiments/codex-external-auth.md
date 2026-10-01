Codex 0.156.0 supports external auth in app-server mode via account/chatgptAuthTokens/refresh.

# Experiment B: Codex app-server external auth

All timestamps are local to this run in UTC. Credential comparisons use only the first eight hexadecimal characters of SHA-256 digests. No credential value is recorded.

## Result

External auth works, but it is an experimental protocol capability in this version. The client must set `capabilities.experimentalApi` to `true` during `initialize`, then call `account/login/start` with type `chatgptAuthTokens`. The app-server keeps those credentials in memory. When an inference request receives HTTP 401, app-server sends the client request `account/chatgptAuthTokens/refresh` with reason `unauthorized`. It does not need a refresh credential in its config directory.

The usable credential digest was `33621478`, the deliberately expired credential digest was `41ab7891`, and the account identifier digest was `a839d5a0`.

## Procedure and observations

- 2026-10-01T02:35:31+00:00: `codex --version` reported `codex-cli 0.156.0`.
- 2026-10-01T02:35:31+00:00: `codex --help` showed `app-server` as an experimental command. Its relevant global options were `-c, --config <key=value>`, `--enable <FEATURE>`, `--disable <FEATURE>`, and `--strict-config`. No external-auth-specific global flag was present.
- 2026-10-01T02:35:31+00:00: `codex app-server --help` showed `--listen <URL>`, `--stdio`, `--code-mode-host <URL>`, `--analytics-default-enabled`, and websocket transport-auth flags `--ws-auth`, `--ws-token-file`, `--ws-token-sha256`, `--ws-shared-secret-file`, `--ws-issuer`, `--ws-audience`, and `--ws-max-clock-skew-seconds`. The websocket flags authenticate the transport, not OpenAI inference. There was no external-auth command-line flag.
- 2026-10-01T02:36:09+00:00: `codex app-server generate-json-schema --experimental` generated the pinned protocol schema in a temporary directory. The schema listed 164 client-to-server request methods and 11 server-to-client request methods. Auth-related client methods were `account/login/start`, `account/login/cancel`, `account/logout`, and `account/read`. The external login variant was type `chatgptAuthTokens`. The auth-related server request was exactly `account/chatgptAuthTokens/refresh`.
- 2026-10-01T02:36:09+00:00: The refresh request schema accepted reason `unauthorized` and optional `previousAccountId`. Its response required `accessToken` and `chatgptAccountId`, with optional `chatgptPlanType`. The external login schema was marked unstable and for internal use only. The generated `account/read` schema said managed mode performs its own refresh flow, while external mode ignores proactive refresh and expects the client to supply credentials again.
- 2026-10-01T02:36:09+00:00: Binary text inspection found the embedded app-server source names and the message `failed to reject unsupported chatgpt auth token refresh request`. No bundled Markdown or JSON documentation was installed beside `/usr/local/bin/codex`. The generated schemas were therefore the exact bundled protocol reference used for the method inventory.
- 2026-10-01T02:38:01+00:00: A mode-check temp `CODEX_HOME` was created with permission 0700. Its `auth.json` was copied from the harness login with the refresh and identity credential fields removed, leaving the access credential and account identifier. File permission was 0600. Directly relying on this stripped managed-login file initialized and started a thread, but inference received HTTP 401 and ended `failed`; removing the identity credential is not tolerated for the existing managed-file mode.
- 2026-10-01T02:39:03+00:00: The first external-login attempt was rejected with JSON-RPC error `-32600`, message `account/login/start.chatgptAuthTokens requires experimentalApi capability`. This established the required initialize capability.
- 2026-10-01T02:40:31+00:00: A fresh temp `CODEX_HOME` with the same stripped file was used. The client initialized with `experimentalApi`, called external login using only the usable access credential and account identifier, started a thread, and sent the one-word prompt `Hi`. Login succeeded, assistant message deltas and completed assistant items arrived, and the thread returned to idle. No refresh credential was available to the process.
- 2026-10-01T02:41:07+00:00: A second fresh process used a syntactically valid copy of the access JWT whose expiry claim was changed to the Unix epoch. External login was accepted. Before and during the turn, app-server sent `account/chatgptAuthTokens/refresh` requests with reason `unauthorized` and the previous account identifier matching digest `a839d5a0`. The experiment client intentionally returned an error instead of replacement credentials; after retries the turn ended `failed`. This demonstrates that app-server asked the connected host to refresh rather than attempting a refresh grant itself.
- 2026-10-01T02:41:07+00:00: Each temporary directory was deleted automatically when its trial ended. The harness login file was never modified.

## Redacted JSON-RPC traffic

The capture below keeps the protocol events needed to reproduce the conclusion. Credential-bearing fields are replaced by SHA-256 prefixes.

```json
{"direction":"client-to-server","id":"init","method":"initialize","params":{"clientInfo":{"name":"fdy0204","version":"1"},"capabilities":{"experimentalApi":true}}}
{"direction":"client-to-server","id":"login","method":"account/login/start","params":{"type":"chatgptAuthTokens","accessToken":"<sha256:33621478>","chatgptAccountId":"<sha256:a839d5a0>"}}
{"direction":"server-to-client","id":"login","result":"success"}
{"direction":"client-to-server","id":"thread","method":"thread/start","params":{"cwd":"/crucible/repo","approvalPolicy":"never","sandbox":"read-only"}}
{"direction":"client-to-server","id":"turn","method":"turn/start","params":{"threadId":"<opaque>","input":[{"type":"text","text":"Hi"}]}}
{"direction":"server-to-client","method":"item/agentMessage/delta","params":"<omitted non-credential payload>"}
{"direction":"server-to-client","method":"thread/status/changed","params":{"status":{"type":"idle"}}}
{"direction":"client-to-server","id":"login","method":"account/login/start","params":{"type":"chatgptAuthTokens","accessToken":"<sha256:41ab7891>","chatgptAccountId":"<sha256:a839d5a0>"}}
{"direction":"server-to-client","id":0,"method":"account/chatgptAuthTokens/refresh","params":{"reason":"unauthorized","previousAccountId":"<sha256:a839d5a0>"}}
{"direction":"client-to-server","id":0,"error":{"code":-32603,"message":"host withheld replacement credentials for experiment"}}
{"direction":"server-to-client","method":"turn/completed","params":{"turn":{"status":"failed"}}}
```

## Interpretation

The copied auth file alone remains managed auth and cannot simply be made external by deleting fields. The supported runtime pattern is protocol-driven: opt into the experimental API, inject the access credential with `account/login/start`, and handle `account/chatgptAuthTokens/refresh` requests in the host. This satisfies the worker design in which app-server never possesses the refresh credential.
