[Skip to main content](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#__docusaurus_skipToContent_fallback)
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
  * [Marketplace Modules](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Marketplace Policies](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Changelog](https://marketplace.gohighlevel.com/docs/Changelog)
  * [Country List](https://marketplace.gohighlevel.com/docs/oauth/country)
  * [FAQs](https://marketplace.gohighlevel.com/docs/oauth/Faqs)
  * [OAuth 2.0](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Business](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Calendars](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Campaigns](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Companies](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Contacts](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Objects](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Associations](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Custom Fields V2](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Conversations](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Courses](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Email](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Forms](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Invoice](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Trigger Links](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Sub-Account (Formerly location)](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Media Storage](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Developer marketplace](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Blogs](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Funnels](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Opportunities](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Payments](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Products](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Saas](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Snapshots](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Social Planner](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Surveys](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Users](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Workflows](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [LC Email](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Custom menus](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Voice AI](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Proposals](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Knowledge Base](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Conversation AI](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Phone System](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Store](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [AI Agent Studio](https://marketplace.gohighlevel.com/docs/sdk/php/index.html)
  * [Webhook Integration Guide](https://marketplace.gohighlevel.com/docs/webhook/WebhookIntegrationGuide)
  * [Webhook Logs Dashboard](https://marketplace.gohighlevel.com/docs/webhook/WebhookLogsDashboard)
  * [Webhook](https://marketplace.gohighlevel.com/docs/category/webhook)


  * [](https://marketplace.gohighlevel.com/docs/)
  * [SDK Overview](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)
  * PHP


On this page
# HighLevel PHP SDK
The `gohighlevel/api-client` composer package is the officially supported SDK for PHP 7.4+ projects. It wraps the full HighLevel API with PSR-18 friendly services, automatic OAuth token rotation, webhook helpers, and pluggable session storage.
## Installation[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#installation "Direct link to Installation")
```
composer require gohighlevel/api-client
```

## Quick Start[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#quick-start "Direct link to Quick Start")
### Initialize with a Private Integration Token[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#initialize-with-a-private-integration-token "Direct link to Initialize with a Private Integration Token")
```
<?phprequire_once __DIR__ . '/vendor/autoload.php';use HighLevel\HighLevel;use HighLevel\HighLevelConfig;$config = new HighLevelConfig([  'privateIntegrationToken' => $_ENV['GHL_PIT'],]);$ghl = new HighLevel($config);
```

### Initialize with OAuth credentials[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#initialize-with-oauth-credentials "Direct link to Initialize with OAuth credentials")
```
use HighLevel\HighLevel;use HighLevel\HighLevelConfig;$config = new HighLevelConfig([  'clientId' => $_ENV['GHL_CLIENT_ID'],  'clientSecret' => $_ENV['GHL_CLIENT_SECRET'],]);$ghl = new HighLevel($config);
```

### Make your first API call[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#make-your-first-api-call "Direct link to Make your first API call")
```
use HighLevel\Services\Contacts\Models\SearchBodyV2DTO;$body = new SearchBodyV2DTO([  'locationId' => 'zBG0T99IsBgOoXUrcROH',  'pageLimit' => 1,]);$contactsResponse = $ghl->contacts->searchContactsAdvanced($body);error_log(json_encode($contactsResponse, JSON_PRETTY_PRINT));
```

## Session storage[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#session-storage "Direct link to Session storage")
Use `HighLevel\Storage\MongoDBSessionStorage` provided by SDK to use mongo as storage or extend it to store tokens in MySQL, PostgreSQL, Redis, etc:
```
<?phpuse HighLevel\HighLevel;use HighLevel\Storage\MongoDBSessionStorage;$sessionStorage = new MongoDBSessionStorage(  $config['mongo_url'],  $config['mongo_db_name'],  $config['collection_name']);$ghl = new HighLevel([  'clientId' => $config['client_id'],  'clientSecret' => $config['client_secret'],  'sessionStorage' => $sessionStorage,  'logLevel' => 'warn']);
```

## Webhook support[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#webhook-support "Direct link to Webhook support")
SDK provides webhook support which can be used as shown below. It will handle INSTALL and UNINSTALL events sent by HighLevel. It will generate token and store it in the db.
```
$payload = $request->getBody()->getContents();$signature = $request->getHeaderLine('x-wh-signature');$ghl->getWebhookManager()->processWebhook(  $payload, // pass raw request body as string here  $signature,  $_ENV['WEBHOOK_PUBLIC_KEY'],  $_ENV['GHL_CLIENT_ID']);
```

Call `verifySignature` directly when you just need validation:
```
$ghl->getWebhookManager()->verifySignature(  $payload,  $signature,  $_ENV['WEBHOOK_PUBLIC_KEY']);
```

## Additional resources[​](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#additional-resources "Direct link to Additional resources")
You can find some SDK & additional examples here:
[SDK](https://github.com/GoHighLevel/highlevel-api-php)
[packagist](https://packagist.org/packages/gohighlevel/api-client)
[Examples](https://github.com/GoHighLevel/ghl-sdk-examples/tree/main/php)
[PreviousPython](https://marketplace.gohighlevel.com/docs/sdk/python)[NextExternal Billing](https://marketplace.gohighlevel.com/docs/oauth/Billing)
  * [Installation](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#installation)
  * [Quick Start](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#quick-start)
    * [Initialize with a Private Integration Token](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#initialize-with-a-private-integration-token)
    * [Initialize with OAuth credentials](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#initialize-with-oauth-credentials)
    * [Make your first API call](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#make-your-first-api-call)
  * [Session storage](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#session-storage)
  * [Webhook support](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#webhook-support)
  * [Additional resources](https://marketplace.gohighlevel.com/docs/sdk/php/index.html#additional-resources)