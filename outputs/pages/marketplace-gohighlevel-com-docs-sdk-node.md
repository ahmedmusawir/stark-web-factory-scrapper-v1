[Skip to main content](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#__docusaurus_skipToContent_fallback)
[![HighLevel Logo](https://marketplace.gohighlevel.com/docs/img/highlevel.png)](https://marketplace.gohighlevel.com/docs/)[Highlevel API 2.0](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
[Sign In](https://marketplace.gohighlevel.com/login)
  * [AI Agents Contest - Guide](https://marketplace.gohighlevel.com/docs/other/AIAgentsGettingStarted)
  * [Getting Started](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
  * [Authorization](https://marketplace.gohighlevel.com/docs/Authorization/authorization_doc)
  * [SDK Overview](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)
    * [Node](https://marketplace.gohighlevel.com/docs/sdk/node)
    * [Python](https://marketplace.gohighlevel.com/docs/sdk/python)
    * [PHP](https://marketplace.gohighlevel.com/docs/sdk/php)
  * [External Billing](https://marketplace.gohighlevel.com/docs/oauth/Billing)
  * [External Authentication](https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication)
  * [User Context in Marketplace Apps](https://marketplace.gohighlevel.com/docs/other/user-context-marketplace-apps)
  * [MCP Server](https://marketplace.gohighlevel.com/docs/other/mcp)
  * [Marketplace Modules](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Marketplace Policies](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Changelog](https://marketplace.gohighlevel.com/docs/Changelog)
  * [Country List](https://marketplace.gohighlevel.com/docs/oauth/country)
  * [FAQs](https://marketplace.gohighlevel.com/docs/oauth/Faqs)
  * [OAuth 2.0](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Business](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Calendars](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Campaigns](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Companies](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Contacts](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Objects](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Associations](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Custom Fields V2](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Conversations](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Courses](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Email](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Forms](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Invoice](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Trigger Links](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Sub-Account (Formerly location)](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Media Storage](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Developer marketplace](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Blogs](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Funnels](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Opportunities](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Payments](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Products](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Saas](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Snapshots](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Social Planner](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Surveys](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Users](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Workflows](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [LC Email](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Custom menus](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Voice AI](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Proposals](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Knowledge Base](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Conversation AI](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Phone System](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Store](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [AI Agent Studio](https://marketplace.gohighlevel.com/docs/sdk/node/index.html)
  * [Webhook Integration Guide](https://marketplace.gohighlevel.com/docs/webhook/WebhookIntegrationGuide)
  * [Webhook Logs Dashboard](https://marketplace.gohighlevel.com/docs/webhook/WebhookLogsDashboard)
  * [Webhook](https://marketplace.gohighlevel.com/docs/category/webhook)


  * [](https://marketplace.gohighlevel.com/docs/)
  * [SDK Overview](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)
  * Node


On this page
# HighLevel Node.js SDK
The official `@gohighlevel/api-client` package wraps every HighLevel REST endpoint with a typed, promise-based interface. You get automatic OAuth handling, token rotation, retries, and consistent errors without re-implementing request plumbing.
## Installation[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#installation "Direct link to Installation")
The SDK supports any modern Node.js runtime (v18+) and works with npm, yarn, or pnpm. Install it as a regular dependency so it is available anywhere you need to talk to HighLevel.
  * npm
  * yarn
  * pnpm


```
npm install @gohighlevel/api-client
```

```
yarn add @gohighlevel/api-client
```

```
pnpm add @gohighlevel/api-client
```

## Quick Start[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#quick-start "Direct link to Quick Start")
### Initialize the client[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#initialize-the-client "Direct link to Initialize the client")
Set your OAuth credentials (or PIT) through environment variables so that local development and deployments share the same configuration.
  * JavaScript
  * TypeScript


```
const{HighLevel}=require('@gohighlevel/api-client');const highLevel =newHighLevel({clientId: process.env.HIGHLEVEL_CLIENT_ID,clientSecret: process.env.HIGHLEVEL_CLIENT_SECRET,});
```

```
import{ HighLevel }from'@gohighlevel/api-client';const highLevel =newHighLevel({ clientId: process.env.HIGHLEVEL_CLIENT_ID??'', clientSecret: process.env.HIGHLEVEL_CLIENT_SECRET??'',});
```

### Make your first API call[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#make-your-first-api-call "Direct link to Make your first API call")
Every service under `highLevel` mirrors the REST resources (contacts, opportunities, workflows, etc.). Provide the required `locationId` or `companyId` so the SDK can manage tokens for you.
```
asyncfunctionlistContacts(){try{const response =await highLevel.contacts.searchContactsAdvanced({locationId:'zBG0T99IsBgOoXUrcROH',pageLimit:5,});console.log(response);}catch(error){console.error('HighLevel error:', error);}}listContacts();
```

## Token storage and refresh[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#token-storage-and-refresh "Direct link to Token storage and refresh")
By default, tokens live in memory. In production, inject your own storage adapter (Redis, MongoDB, SQL, etc.) so tokens survive restarts:
```
import{HighLevel,MongoDBSessionStorage}from'@gohighlevel/api-client';const highLevel =newHighLevel({clientId: process.env.HIGHLEVEL_CLIENT_ID,clientSecret: process.env.HIGHLEVEL_CLIENT_SECRET,sessionStorage:newMongoDBSessionStorage({dbUrl:'mongodb://localhost:27017',dbName:'ghl_sessions'})});
```

The SDK will refresh expired access tokens on-demand and update your storage without extra work.
## Webhook middleware[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#webhook-middleware "Direct link to Webhook middleware")
Use `highLevel.webhooks.subscribe()` to get an Express-compatible middleware that validates signatures, handles INSTALL/UNINSTALL events, and keeps session storage synchronized before your custom logic runs.
```
app.use('/api/webhooks/ghl', highLevel.webhooks.subscribe());app.post('/api/webhooks/ghl',(req, res)=>{// Your business logic can rely on the tokens being current. res.json({ok:true});});
```

**Note** : If you use webhook middleware provided by SDK, in case of bulk installation it will generate and store the token for each location when it receives INSTALL event from highlevel.
## Additional resources[​](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#additional-resources "Direct link to Additional resources")
You can find some SDK & additional examples here:
[SDK](https://github.com/GoHighLevel/highlevel-api-sdk)
[npm](https://www.npmjs.com/package/@gohighlevel/api-client)
[Examples](https://github.com/GoHighLevel/ghl-sdk-examples/tree/main/node)
[PreviousGetting Started with HighLevel SDKs](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)[NextPython](https://marketplace.gohighlevel.com/docs/sdk/python)
  * [Installation](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#installation)
  * [Quick Start](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#quick-start)
    * [Initialize the client](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#initialize-the-client)
    * [Make your first API call](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#make-your-first-api-call)
  * [Token storage and refresh](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#token-storage-and-refresh)
  * [Webhook middleware](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#webhook-middleware)
  * [Additional resources](https://marketplace.gohighlevel.com/docs/sdk/node/index.html#additional-resources)