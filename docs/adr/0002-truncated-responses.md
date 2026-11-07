# ADR-0002: Return Truncated Responses Flagged and Do Not Cache Them

## Status

Proposed — November 3, 2026

## Context

When making an LLM API call, we specify a maximum token limit in the LLMRequest. If the model reaches this limit before completing its response, generation stops and the response contains `stop_reason` == `max_tokens`, indicating that the response may be incomplete.

This stop reason is already captured in our LLMResponse object. The LoggingClient also records it in the log, but currently does not take any action based on it.

The LLMResponse object already has a `truncated` property that indicates whether the response is `truncated`. Currently, the `CachingClient` caches every response, including `truncated` responses. ADR-0001 establishes that detecting truncation is the responsibility of the client layer.

The responsibility for deciding how to use or otherwise handle a `truncated` response currently falls to the consuming client. However, we do not yet know how frequently this happens or how significantly it affects downstream processing. Therefore, the severity and impact of this issue are not yet clear.

Assumptions: Partial responses may be useful to some callers, and truncation is expected to be infrequent. Neither assumption has been validated with actual caller usage or production data.

## Decision

We keep: the response is returned with the `truncated` property.
We add: `CachingClient` does not write a `truncated` response to the cache.

We chose this approach because it is the smallest change that prevents a `truncated` response from being cached and repeatedly served to subsequent callers. Since we do not yet have a real consuming client, we have no evidence to justify introducing stricter error handling or automatic retries. Returning the response with the `truncated` property preserves the caller's flexibility to decide how to handle it.

The risk with this approach is that the calling application may not check `truncated`. As a result, an incomplete response could be processed or delivered to the user without anyone noticing.

At this point, we do not know how frequently this happens or whether it presents a significant problem. If we find that it causes issues, we can revisit this decision and consider the alternatives below.

The truncation check will happen inside the `CachingClient`, before the response is saved to the cache. When the response is `truncated`, `CachingClient` will return it to the caller without caching it. This prevents an incomplete response from being repeatedly served from the cache.

**How we will test this:**
- Add a unit test where the fake inner client returns a response with `stop_reason` == `max_tokens`. Call `complete()` twice with the same request and verify that the inner client is called twice and the response is returned both times. Optionally, verify that no cache file is created.

## Alternatives considered

**Option 0: Return and flag, do not cache (selected)**

**Pros**
- The caller receives the response and can decide whether the partial response is usable.
- The `truncated` property allows the caller to identify incomplete responses.
- Prevents `truncated` responses from being cached and repeatedly served to subsequent callers.
- No automatic retries are introduced.

**Cons**
- The caller must check the `truncated` property to identify incomplete responses.
- Different consuming applications may handle `truncated` responses differently, leading to inconsistent behavior.

**Option 1: Raise an error**

**Pros**
- A `truncated` answer can never reach a user unnoticed because the caller must handle the error before proceeding.

**Cons**
- Some use cases may be able to work with partial responses. Raising an error would prevent callers from receiving the response through the normal return path, even when the partial response is useful.

**Option 2: Warn and return as is**

**Pros**
- The response is still returned to the caller, allowing them to decide what action to take. A warning is also logged to indicate that the response was `truncated`.

**Cons**
- LoggingClient already records `stop_reason` for every completed call. Adding a separate warning would duplicate information already available in the logs without providing additional protection against `truncated` responses reaching users.

- The caller may still fail to notice the warning, and the `truncated` response could reach the user without being handled.

**Option 3: Retry with a bigger limit**

**Pros**
- The caller may get a complete answer without writing any truncation-handling code.

**Cons**
- The downside is that this introduces additional API cost and increases response latency. It also does not guarantee that the response will be complete on the retry.


## Consequences

**What gets easier**
- The caller receives the response even when it is `truncated` and can decide whether the partial response is usable.
- No automatic retries are introduced to handle truncation.
- The caller has the flexibility to handle truncation based on its specific use case.

**What gets harder and remains our responsibility**
- The caller must check the `truncated` property to identify incomplete responses. If it does not, incomplete responses may be processed or delivered to users without being noticed.
- Different consuming applications may handle `truncated` responses differently, leading to inconsistent behavior.
- We need to monitor how frequently truncation occurs and understand its impact on downstream processing.
- Since `truncated` responses are not cached, repeated identical requests will call the model again, resulting in additional API costs and latency. The caller should increase `max_tokens` and retry the request to obtain a complete response. The `truncated` response is unlikely to be useful for subsequent processing.

**What would make us revisit the decision**
- If more than 5% of completed LLM calls where cached is false have `truncated` set to true over a rolling seven-day period, based on the `LoggingClient` JSONL logs, we will revisit this decision.
