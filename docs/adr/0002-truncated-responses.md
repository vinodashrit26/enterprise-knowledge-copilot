# ADR-0002: Handle Response Truncation (stop_reason == "max_tokens")

## Status

Proposed — Nov 3, 2026

## Context

When making an LLM API call, we specify a maximum token limit in the LLMRequest. If the model reaches this limit before completing its response, generation stops and the response contains stop_reason == "max_tokens", indicating that the response may be incomplete.

This stop reason is already captured in our LLMResponse object. The LoggingClient also records it in the log, but currently does not take any action based on it.

The LLMResponse object already has a `truncated` property that indicates whether the response is truncated.Currently, the CachingClient caches every response, including truncated responses. ADR-0001 establishes that detecting truncation is the responsibility of the client layer.

The responsibility for deciding how to use or otherwise handle a truncated response currently falls to the consuming client. However, we do not yet know how frequently this happens or how significantly it affects downstream processing. Therefore, the severity and impact of this issue are not yet clear.

## Decision
When the LLM returns a response with stop_reason == "max_tokens", we will return the response along with the stop reason to the caller. This allows the caller to check whether the response is truncated and decide how to handle it.

We chose this approach because the API cost has already been incurred, regardless of how we handle the truncated response. Returning the response gives the caller the flexibility to decide whether the partial response is still useful or whether further action is needed.

The risk with this approach is that the calling application may not check stop_reason. As a result, an incomplete response could be processed or delivered to the user without anyone noticing.

At this point, we do not know how frequently this happens or whether it presents a significant problem. If we find that it causes issues, we can revisit this decision and consider the alternatives below

The truncation check will happen inside the CachingClient, before the response is saved to the cache. If the response is truncated, CachingClient will return it to the caller without caching it. This prevents an incomplete response from being repeatedly served from the cache. The caller can then use the `truncated` property to decide how to handle the response.

**How we will test this:**
- Add a unit test where the fake inner client returns a response with `stop_reason == "max_tokens"`. Verify that the response is returned to the caller and is not saved in the cache.

## Alternatives considered
**Option 1: Raise an error**

**Pros**
- Forces the caller to handle truncation explicitly by raising a TruncatedResponseError when stop_reason == "max_tokens".

**Cons**
- The downside is that some use cases may be able to work with partial responses. Raising an error would prevent callers from receiving the response through the normal return path, even when the partial response is useful.
- The API cost would still have been incurred.

**Option 2: Warn and return as is**

**Pros**
- The response is still returned to the caller, allowing them to decide what action to take. A warning is also logged to indicate that the response was truncated.

**Cons**
- The downside is that the caller may not check the log file or notice the warning. As a result, an incomplete response could reach the user without anyone being aware of the truncation.

**Option 3: Retry with a bigger limit**

**Pros**
Automatically retries with a higher token limit when stop_reason == "max_tokens" is received, giving the model another opportunity to generate a complete response.

**Cons**
The downside is that this introduces additional API cost and increases response latency. It also does not guarantee that the response will be complete on the retry.


## Consequences

**What gets easier**
- The caller receives the response even when it is truncated and can decide whether the partial response is usable.
- No additional API calls, cost, or latency are introduced to handle truncation.
- The caller has the flexibility to handle truncation based on its specific use case.

**What gets harder and remains our responsibility**
- The caller must check stop_reason == "max_tokens" to identify truncated responses. If it does not, incomplete responses may be processed or delivered to users without being noticed.
- Different consuming applications may handle truncated responses differently, leading to inconsistent behavior.
- We need to monitor how frequently truncation occurs and understand its impact on downstream processing.

**What would make us revisit the decision**
- If truncated responses frequently cause downstream processing failures.
- If incomplete responses reach users and negatively affect their experience.
- If we find that consuming applications are not consistently checking stop_reason and handling truncation appropriately.
- If usage data shows that truncation is more frequent or has a greater impact than initially expected.
- If more than 5% of LLM responses are truncated over a representative monitoring period, investigate whether additional handling is needed.
