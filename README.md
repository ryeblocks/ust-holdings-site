# U.S. Treasury Holdings Dashboard

Public dashboard comparing TIC major foreign holders of U.S. Treasuries with stablecoin and tokenized U.S. treasury exposure.

## Sources

- U.S. Treasury TIC Major Foreign Holders
- Issuer attestation / reserve reports
- RWA.xyz tokenized treasury market data

## Deploy

Static site for Vercel. No build step — `index.html` is the full app.

## Update flow

Rebuild the dashboard locally from the research pipeline, copy the scrubbed HTML to this repo as `index.html`, then push. Vercel redeploys automatically.
