[Skip to main content](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#__docusaurus_skipToContent_fallback)
[![HighLevel Logo](https://marketplace.gohighlevel.com/docs/img/highlevel.png)](https://marketplace.gohighlevel.com/docs/)[Highlevel API 2.0](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
[Sign In](https://marketplace.gohighlevel.com/login)
  * [AI Agents Contest - Guide](https://marketplace.gohighlevel.com/docs/other/AIAgentsGettingStarted)
  * [Getting Started](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
    * [Agency vs Sub-Account](https://marketplace.gohighlevel.com/docs/oauth/AgencyVsSubAccount)
    * [App Distribution](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution)
  * [Authorization](https://marketplace.gohighlevel.com/docs/Authorization/authorization_doc)
  * [SDK Overview](https://marketplace.gohighlevel.com/docs/sdk/GettingStartedSDK)
  * [External Billing](https://marketplace.gohighlevel.com/docs/oauth/Billing)
  * [External Authentication](https://marketplace.gohighlevel.com/docs/oauth/ExternalAuthentication)
  * [User Context in Marketplace Apps](https://marketplace.gohighlevel.com/docs/other/user-context-marketplace-apps)
  * [MCP Server](https://marketplace.gohighlevel.com/docs/other/mcp)
  * [Marketplace Modules](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Marketplace Policies](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Changelog](https://marketplace.gohighlevel.com/docs/Changelog)
  * [Country List](https://marketplace.gohighlevel.com/docs/oauth/country)
  * [FAQs](https://marketplace.gohighlevel.com/docs/oauth/Faqs)
  * [OAuth 2.0](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Business](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Calendars](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Campaigns](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Companies](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Contacts](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Objects](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Associations](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Custom Fields V2](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Conversations](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Courses](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Email](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Forms](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Invoice](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Trigger Links](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Sub-Account (Formerly location)](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Media Storage](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Developer marketplace](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Blogs](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Funnels](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Opportunities](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Payments](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Products](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Saas](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Snapshots](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Social Planner](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Surveys](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Users](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Workflows](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [LC Email](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Custom menus](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Voice AI](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Proposals](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Knowledge Base](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Conversation AI](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Phone System](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Store](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [AI Agent Studio](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html)
  * [Webhook Integration Guide](https://marketplace.gohighlevel.com/docs/webhook/WebhookIntegrationGuide)
  * [Webhook Logs Dashboard](https://marketplace.gohighlevel.com/docs/webhook/WebhookLogsDashboard)
  * [Webhook](https://marketplace.gohighlevel.com/docs/category/webhook)


  * [](https://marketplace.gohighlevel.com/docs/)
  * [Getting Started](https://marketplace.gohighlevel.com/docs/oauth/GettingStarted)
  * App Distribution


On this page
# Marketplace App Distribution Model
This guide covers the new, simplified Marketplace distribution model and the OAuth flow you’ll need to implement to obtain the correct access tokens.
## App Distribution Model[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#app-distribution-model "Direct link to App Distribution Model")
To configure your desired app distribution model, you have three fields:
Field| Values| Description  
---|---|---  
**Who is the target user of the app?**| `Agency` / `Sub-account`| Who is going to interact with the app? In other words, whose access token does the app ultimately need? For most apps, this will be `Sub-account` (Recommended). **Note:** This field cannot be modified once set.  
**Who can install the app?**| `Both Agency and Sub-account` / `Agency Only`| Which user(s) may see and install the app from the Marketplace UI? Recommended: “Both Agency & Sub-account” for maximum reach. Use "Agency Only" for fully white-labelled SaaS features only agencies can discover and install.  
**Can this app be bulk-installed by agencies?**| `Yes` / `No`| Primarily for backwards compatibility. All new Marketplace apps will be set to `Yes` (mandatory). Allows agency owners/admins to install to multiple sub-accounts in one operation. Cannot revert to `No` once set.  
## Distribution Scenarios[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#distribution-scenarios "Direct link to Distribution Scenarios")
### Developer’s distribution config scenarios and getting the right access token[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#developers-distribution-config-scenarios-and-getting-the-right-access-token "Direct link to Developer’s distribution config scenarios and getting the right access token")
Who is the target user?| Who can install the app?| Can the app be bulk-installed by agencies?| User Installation Scenarios| Access Token Details| Step 2  
---|---|---|---|---|---  
Agency| N/A| N/A| Agency user installs the app| `“isBulkInstallation” : false`, `“userType” : ”Company”`| N/A  
Sub-account| Agency & sub-account| No| Sub-account user installs the app| `“isBulkInstallation” : false`, `“userType” : ”Location”`| N/A  
Sub-account| Agency & sub-account| No| Agency user installs the app| `“isBulkInstallation” : false`, `“userType" : "Location”`| N/A  
Sub-account| Agency & sub-account| Yes| Sub-account user installs the app| `“isBulkInstallation” : false`, `“userType" : "Location”`| N/A  
Sub-account| Agency & sub-account| Yes| [NEW and RECOMMENDED] Agency user installs the app| `“isBulkInstallation” : true`, `“userType" : "Company”`| **1.** [Get sub-accounts where app is installed](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-installed-location/index.html) **2.** [Get Location Token using Agency Token](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-location-access-token/index.html) for every location where app is installed **3.** Listen to [AppInstall webhook](https://marketplace.gohighlevel.com/docs/webhook/AppInstall) event for automatic future installations or installs done as part of a SaaS plan, and [Get Location Token using Agency Token](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-location-access-token/index.html) for the newly installed locations.  
Sub-account| Agency Only| Yes| Agency user installs the app| `“isBulkInstallation” : true`, `“userType" : "Company"`| **1.** [Get sub-accounts where app is installed](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-installed-location/index.html) **2.** [Get Location Token using Agency Token](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-location-access-token/index.html) for every location where app is installed **3.** Listen to [AppInstall webhook](https://marketplace.gohighlevel.com/docs/webhook/AppInstall) event for automatic future installations or installs done as part of a SaaS plan, and [Get Location Token using Agency Token](https://marketplace.gohighlevel.com/docs/ghl/oauth/get-location-access-token/index.html) for the newly installed locations.  
## Backward Compatibility[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#backward-compatibility "Direct link to Backward Compatibility")
To maintain the existing installation flow for legacy apps, mappings are set as follows:
Legacy Distribution Type| Target User| Installer| Bulk-install| Recommendations  
---|---|---|---|---  
Agency Only| Agency| N/A| N/A| N/A  
Sub-account Only| Sub-account| Agency & Sub-account| No| Develop the token exchange mechanism for bulk-installation flow as mentioned above. Once done, set "Can the app be bulk-installed by agencies?" to "Yes"  
Agency & Sub-account| Sub-account| Agency Only| Yes| To make the app accessible to sub-accounts, you must ensure the app does not require any agency-level access such as: Agency Level Scopes - companies.readonly, companies.write, location.write, saas/location.write, snapshots.readonly, snapshots.write, custom-menu-link.readonly, custom-menu-link.write. Module > Snapshots, Module > CustomJS. If your app does not require any of the above: 1. Develop the OAuth flow for installation by sub-account admins, which would generate a userType: Location token, as mentioned above. 2. Once done, change "Who can install the app?" to "Agency & sub-account"  
## Target User Types[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-types "Direct link to Target User Types")
### Target User: Agency[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-agency "Direct link to Target User: Agency")
Choose this if your app is only relevant for agency-level accounts.
![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155048583581/original/w4Mv3eWxtc7ky1cU_fU1FfLuBdg8fYAt_w.png?1750392548)
  * **App Listing:** Only in agency Marketplace.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155048583594/original/f4TxfrBHaJTtETQV7pYDWWQ4nI5z7bz-vw.png?1750392601)
  * **Installation:** Only agency admins/owners can install/uninstall.
  * **Payments:** Agency bears cost for paid apps.
  * **Re-selling:** Not available to sub-accounts.


### Target User: Sub-account — Both Can Install[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-sub-account--both-can-install "Direct link to Target User: Sub-account — Both Can Install")
Choose this if your app is for sub-account-level usage but should be installable by both agencies and sub-accounts.
![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155048583624/original/kJtU4fEgullilWG0fxoAnDDRM-hJdD-cdg.png?1750392750)
  * **App Listing:** Appears in both agency and sub-account Marketplaces.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155048583635/original/eYRbavl9kxE3dTmJWUzJ26BuxrtACE9o4g.png?1750392836)
  * **Installation:** Both sub-account admins and agency admins can install.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155023404538/original/lQxf69LOM8uFEPOdE9MQ6M8gYq-b4GDkoA.png?1711222807)
  * **Bulk Installation:** Supported if enabled. Agencies can auto-install to all sub-accounts.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155023404499/original/MqHiBlSiuQlJPZxBKZ49b7ZdsXzUeYZ6tw.png?1711222532)
  * **Payments:** Sub-account pays for paid apps.
  * **Re-selling:** Agencies can re-sell.


### Target User: Sub-account — Only Agency Can Install[​](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-sub-account--only-agency-can-install "Direct link to Target User: Sub-account — Only Agency Can Install")
Choose this if only agencies should install, but app is used at sub-account level.
![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155048584235/original/ifH_YbCWG2-uY5wxZFLw6jeWGAm3Ma0PpQ.png?1750394316)
  * **App Listing:** Only in agency view.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155023404478/original/ZaZlYBRJIocjPL0AfUJkH_yXBSpC_BEoWg.png?1711222458)
  * **Installation:** Agency admins/owners install/uninstall for sub-accounts.
  * **Bulk Installation:** Supported if enabled.


![drawing](https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/155023404499/original/MqHiBlSiuQlJPZxBKZ49b7ZdsXzUeYZ6tw.png?1711222532)
  * **Re-selling:** Agencies can re-sell with markup.


## Share your feedback
★★★★★
[PreviousAgency vs Sub-Account](https://marketplace.gohighlevel.com/docs/oauth/AgencyVsSubAccount)[NextAuthorization](https://marketplace.gohighlevel.com/docs/Authorization/authorization_doc)
  * [App Distribution Model](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#app-distribution-model)
  * [Distribution Scenarios](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#distribution-scenarios)
    * [Developer’s distribution config scenarios and getting the right access token](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#developers-distribution-config-scenarios-and-getting-the-right-access-token)
  * [Backward Compatibility](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#backward-compatibility)
  * [Target User Types](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-types)
    * [Target User: Agency](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-agency)
    * [Target User: Sub-account — Both Can Install](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-sub-account--both-can-install)
    * [Target User: Sub-account — Only Agency Can Install](https://marketplace.gohighlevel.com/docs/oauth/AppDistribution/index.html#target-user-sub-account--only-agency-can-install)