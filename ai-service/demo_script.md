# AI Demo Script

## Live Inputs

### Describe

Input:

```json
{
  "input_text": "Port congestion is delaying supplier A shipments by five days."
}
```

Expected outcome:

- Returns a short structured description
- Includes `generated_at`
- Includes `model`

Latest live output example:

```json
{
  "description": "Port congestion is currently impacting the supply chain, resulting in delayed shipments from supplier A. The congestion is causing a delay of approximately five days, which may affect the overall delivery timeline. This disruption can potentially lead to increased costs and reduced customer satisfaction. As a result, the business may need to explore alternative shipping routes or suppliers to mitigate the risk of further delays.",
  "generated_at": "2026-05-07T12:11:59.598873+00:00",
  "is_fallback": false,
  "model": "llama-3.3-70b-versatile"
}
```

### Recommend

Input:

```json
{
  "input_text": "Critical inbound delay from supplier B is affecting production scheduling."
}
```

Expected outcome:

- Returns exactly 3 recommendations
- Each recommendation includes `action_type`, `description`, and `priority`

Latest live output example:

```json
[
  {
    "action_type": "mitigate",
    "description": "Diversify the supplier base to reduce dependence on supplier B and minimize the impact of future delays.",
    "priority": "high"
  },
  {
    "action_type": "review",
    "description": "Analyze the contract with supplier B to identify potential clauses for renegotiation or penalties for non-compliance with delivery schedules.",
    "priority": "medium"
  },
  {
    "action_type": "communicate",
    "description": "Notify downstream stakeholders and customers of potential production delays and provide regular updates on the status of the inbound shipment from supplier B.",
    "priority": "low"
  }
]
```

### Generate Report

Input:

```json
{
  "input_text": "Create a report for port congestion and missed vessel connections."
}
```

Expected outcome:

- Returns `title`, `summary`, `overview`, `key_items`, and `recommendations`
- Includes fallback flag when Groq is unavailable

Latest live output example:

```json
{
  "generated_at": "2026-05-07T12:12:01.290718+00:00",
  "is_fallback": false,
  "key_items": [
    "Increased cargo volume",
    "Inadequate port infrastructure",
    "Inefficient terminal operations"
  ],
  "model": "llama-3.3-70b-versatile",
  "overview": "Port congestion occurs when the volume of cargo exceeds the port's capacity to handle it, resulting in delays and missed connections. This can be caused by various factors, including increased demand, inadequate port infrastructure, and inefficient operations.",
  "recommendations": [
    "Invest in port infrastructure upgrades",
    "Implement efficient terminal operating systems",
    "Diversify shipping routes to reduce reliance on congested ports"
  ],
  "summary": "Port congestion has resulted in missed vessel connections, leading to delays and increased costs. This report highlights the key factors contributing to the congestion and provides recommendations for mitigation. Immediate action is necessary to minimize the impact on supply chains.",
  "title": "Port Congestion Risk Report"
}
```

## Health Check

Expected outcome:

- Returns service status
- Returns current model name
- Returns average response time and uptime

Latest live output example:

```json
{
  "avg_response_time_ms": 0.0,
  "model": "llama-3.3-70b-versatile",
  "status": "ok",
  "uptime_seconds": 2.01
}
```

## 60-Second Tech Explanation

The AI service is a Flask microservice that receives sanitized request data, applies rate limiting, and calls Groq with structured prompt templates. The service asks Groq to return strict JSON so the rest of the application gets predictable output for descriptions, recommendations, and reports. If the live model fails, the service returns safe fallback responses instead of breaking the workflow.

## Delivery Note

The live AI service and endpoint checks were verified locally. Full browser/demo-machine and full-stack container rehearsal still depend on the unfinished backend/frontend pieces and a Docker-enabled environment.
