[Skip to main content](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#__docusaurus_skipToContent_fallback)
[![HighLevel Logo](https://marketplace.gohighlevel.com/docs/img/highlevel.png)](https://marketplace.gohighlevel.com/docs/)[Highlevel API 2.0](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
[Sign In](https://marketplace.gohighlevel.com/login)
  * [AI Agents Contest - Guide](https://marketplace.gohighlevel.com/docs/other/AIAgentsGettingStarted)
  * [Getting Started](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
  * [Authorization](https://marketplace.gohighlevel.com/docs/Authorization/authorization_doc)
  * [SDK Overview](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)
  * [External Billing](https://marketplace.gohighlevel.com/docs/oauth/Billing)
  * [External Authentication](https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication)
  * [User Context in Marketplace Apps](https://marketplace.gohighlevel.com/docs/other/user-context-marketplace-apps)
  * [MCP Server](https://marketplace.gohighlevel.com/docs/other/mcp)
  * [Marketplace Modules](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Marketplace Policies](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Changelog](https://marketplace.gohighlevel.com/docs/Changelog)
  * [Country List](https://marketplace.gohighlevel.com/docs/oauth/country)
  * [FAQs](https://marketplace.gohighlevel.com/docs/oauth/Faqs)
  * [OAuth 2.0](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Business](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Calendars](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Campaigns](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Companies](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Contacts](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Objects](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Associations](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Custom Fields V2](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Conversations](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Courses](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Email](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Forms](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Invoice](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Trigger Links](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Sub-Account (Formerly location)](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Media Storage](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Developer marketplace](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Blogs](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Funnels](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Opportunities](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Payments](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Products](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Saas](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Snapshots](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Social Planner](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Surveys](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Users](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Workflows](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [LC Email](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Custom menus](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Voice AI](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Proposals](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Knowledge Base](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Conversation AI](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Phone System](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Store](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [AI Agent Studio](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html)
  * [Webhook Integration Guide](https://marketplace.gohighlevel.com/docs/webhook/WebhookIntegrationGuide)
  * [Webhook Logs Dashboard](https://marketplace.gohighlevel.com/docs/webhook/WebhookLogsDashboard)
  * [Webhook](https://marketplace.gohighlevel.com/docs/category/webhook)


  * [](https://marketplace.gohighlevel.com/docs/)
  * External Billing


On this page
# Billing Webhook
This webhook is essential for externally billed apps within our marketplace. It must be accessed by developers to authorize the installation of the app.
The primary purpose of this webhook is to capture and update payment information for apps that employ a Paid business model and do not utilize HighLevel's internal billing mechanism.
## 1. Prerequisites for using this webhook[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#1-prerequisites-for-using-this-webhook "Direct link to 1. Prerequisites for using this webhook")
Before using this webhook, ensure that you meet the following prerequisites on the [Marketplace](https://marketplace.gohighlevel.com):
  1. You should have an app with a Business Model marked as Paid.
  2. External Billing must be enabled for your app.
  3. You must have entered the Billing URL.


## 2. Retrieving Parameters from the Billing URL[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#2-retrieving-parameters-from-the-billing-url "Direct link to 2. Retrieving Parameters from the Billing URL")
When an Agency or Location installs your app, they will be redirected to the Billing URL specified in the configuration. You will receive the following parameters in the URL:
Parameter Name| Possible Values| Notes  
---|---|---  
clientId| `<client_id>`| Used for validation.  
installType| `location`, `agency`| You will receive `agency,location` in case of both agency and location.  
locationId| `<location_id>`| You will receive this in case of `location` or `agency,location`.  
companyId| `<agency_id>`| You will receive this in case of `agency` or `agency,location`.  
## 3. Using The Webhook[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#3-using-the-webhook "Direct link to 3. Using The Webhook")
After successfully processing the payment on your end, you need to make a request to our billing webhook endpoint:
```
https://services.leadconnectorhq.com/oauth/billing/webhook
```

The parameters you need to include in the webhook request are as follows:
**Request Method:** POST
**Request Headers:**
Name| Value| Notes  
---|---|---  
x-ghl-client-key| Your client key| This should be from the same client for which you are authorizing the payment.  
x-ghl-client-secret| Your Client Secret| The corresponding client secret for the client key used.  
Content-Type| application/json|   
**Request Body:**
Name| Value| Notes  
---|---|---  
clientId| Your client ID|   
authType| Enum| Possible values are `company` and `location`.  
locationId| `<location_id>`| Required when authType is `location`.  
companyId| `<company_id>`| Required when authType is `company`.  
subscriptionId| Your subscription ID| You can include this if you have configured a subscription model.  
paymentId| Your Payment ID| In case of a one-time payment model, you can send this parameter.  
amount| Billed Amount| Required.  
status| Enum| Possible values are `COMPLETED` and `FAILED`.  
paymentType| Enum| Possible values are `one_time` and `recurring`.  
### Example[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#example "Direct link to Example")
Here is a sample cURL command for the webhook request:
```
curl --location 'https://services.leadconnectorhq.com/oauth/billing/webhook' \--header 'x-ghl-client-key: <client_key>' \--header 'x-ghl-client-secret: <client_secret>' \--header 'Content-Type: application/json' \--data '{  "clientId": "<client_id>",  "authType": "location",  "locationId": "<location_id>",  "subscriptionId": "<subscription_id>",  "paymentId": "<payment_id>",  "amount": 12,  "status": "COMPLETED",  "paymentType": "recurring"}'
```

## Webhook FAQs[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#webhook-faqs "Direct link to Webhook FAQs")
### Can I get multiple location ids in the Billing URL?[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#can-i-get-multiple-location-ids-in-the-billing-url "Direct link to Can I get multiple location ids in the Billing URL?")
Yes, in the case of multiple installations, you will receive a list of locationIds in a comma-separated format in the billing URL.
### Can I update for multiple locations in one call?[​](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#can-i-update-for-multiple-locations-in-one-call "Direct link to Can I update for multiple locations in one call?")
No, you need to trigger the webhook for each location and company separately.
## Share your feedback
★★★★★
[PreviousPHP](https://marketplace.gohighlevel.com/docs/sdk/php)[NextExternal Authentication](https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication)
  * [1. Prerequisites for using this webhook](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#1-prerequisites-for-using-this-webhook)
  * [2. Retrieving Parameters from the Billing URL](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#2-retrieving-parameters-from-the-billing-url)
  * [3. Using The Webhook](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#3-using-the-webhook)
    * [Example](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#example)
  * [Webhook FAQs](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#webhook-faqs)
    * [Can I get multiple location ids in the Billing URL?](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#can-i-get-multiple-location-ids-in-the-billing-url)
    * [Can I update for multiple locations in one call?](https://marketplace.gohighlevel.com/docs/oauth/Billing/index.html#can-i-update-for-multiple-locations-in-one-call)