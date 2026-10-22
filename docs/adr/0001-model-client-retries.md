# ADR-0001: Use the SDK's Built-in Retries

## Status

Accepted — October 22, 2026

## Context

Our application calls a language model through the Anthropic SDK. Requests can fail because of temporary issues such as connection problems, rate limits, timeouts, or server errors. Retrying these failures can improve reliability, but excessive retries can increase latency and place additional load on the service.

The Anthropic SDK provides built-in retry handling with exponential backoff and support for the server's `Retry-After` hint. Its default is two retries, meaning up to three attempts in total. The default request timeout is 10 minutes, which is too long for an interactive copilot. The SDK allows us to configure `max_retries` and `timeout` on the client.

## Decision

We will use the Anthropic SDK's built-in retry mechanism rather than implement our own. We will explicitly set `max_retries=2` (the current default, pinned explicitly to protect against default changes in future SDK upgrades) and an initial `timeout=60` seconds. We will review the timeout after measuring Haiku and Sonnet latency in Week 2, taking `max_tokens` into account.

## Alternatives considered

**Option 1: Use the SDK's built-in retries (selected)**

**Pros**
- Reuses existing retry handling and exponential backoff.
- Reduces custom implementation, testing, and maintenance.
- Allows retry attempts and request timeouts to be configured explicitly.

**Cons**
- Offers less control over retry behavior than a custom implementation.
- Individual retry attempts may require additional logging or instrumentation for troubleshooting.

**Option 2: Implement our own retry mechanism (rejected)**

**Pros**
- Provides control over retry conditions, limits, backoff strategy, and logging.
- Allows retry behavior to be changed independently of the SDK.

**Cons**
- Requires additional implementation, testing, and maintenance.
- Introduces the risk of defects in our retry logic.
- Duplicates functionality already provided by the SDK.

Adding a custom retry layer on top of the SDK's retries could multiply attempts. For example, three attempts at each layer could result in up to nine underlying attempts for one operation. The SDK already provides the retry behavior we currently need, so this additional complexity is not justified.

## Consequences

**What gets easier**
- We can rely on the SDK for retry handling and focus on application business logic.
- Explicit configuration makes our intended retry count and timeout clear. The `uv.lock` file pins the Anthropic SDK dependency to version `1.17.0` for reproducible dependency resolution.

**What gets harder and remains our responsibility**
- With a 60-second timeout per attempt and two retries, repeated timeouts could take approximately three minutes plus backoff delays. This is not a strict upper bound because server-provided retry delays can affect the total duration.
- Caching, cost logging, and detecting truncated model responses remain responsibilities of our client layer.
- We do not yet have a confirmed measurement of the percentage of calls that require retries. As a follow-up, we will investigate SDK logging and add client-level instrumentation if needed to record retry counts reliably.

**What would make us revisit the decision**
- More than 5% of model calls require retries over a representative seven-day period, as measured through SDK logging or client-level instrumentation, and investigation shows the current policy is insufficient.
- The timeout causes legitimate requests to fail or allows requests to occupy resources for too long.
- We need retry behavior or observability that the SDK cannot provide through configuration or instrumentation.
