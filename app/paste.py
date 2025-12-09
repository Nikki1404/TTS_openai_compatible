Hi Ankit,

Swagger and the /apps/* endpoints are not loading because the requests are being blocked at the Imperva (Incapsula) WAF layer, before they reach AWS.

Curl responses show Imperva block signatures:

“Request unsuccessful / Incapsula incident ID”

x-iinfo, visid_incap, incap_ses headers

This confirms the traffic never reaches the ALB, target group, or FastAPI — which is why the backend works internally but not externally.

Required Action

Please add a WAF bypass/whitelist rule in Imperva for:

/apps/*


to allow this API path to pass without WAF inspection.

Once applied, Swagger UI and external API access will work normally.
