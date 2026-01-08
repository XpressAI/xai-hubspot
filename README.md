<p align="center">
  <a href="https://github.com/XpressAI/xircuits/tree/master/xai_components#xircuits-component-library-list">Component Libraries</a> •
  <a href="https://github.com/XpressAI/xircuits/tree/master/project-templates#xircuits-project-templates-list">Project Templates</a>
  <br>
  <a href="https://xircuits.io/">Docs</a> •
  <a href="https://xircuits.io/docs/Installation">Install</a> •
  <a href="https://xircuits.io/docs/category/tutorials">Tutorials</a> •
  <a href="https://xircuits.io/docs/category/developer-guide">Developer Guides</a> •
  <a href="https://github.com/XpressAI/xircuits/blob/master/CONTRIBUTING.md">Contribute</a> •
  <a href="https://www.xpress.ai/blog/">Blog</a> •
  <a href="https://discord.com/invite/vgEg2ZtxCw">Discord</a>
</p>

<p align="center"><i>Xircuits Component Library for HubSpot – Seamlessly integrate HubSpot CRM into your automation workflows.</i></p>

---

## Xircuits Component Library for HubSpot

Integrate HubSpot CRM capabilities into your Xircuits workflows. This library provides components for managing contacts, companies, deals, engagements, and more through the HubSpot API.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Main Xircuits Components](#main-xircuits-components)
  - [Client](#client)
  - [Contacts](#contacts)
  - [Companies](#companies)
  - [Deals](#deals)
  - [Associations](#associations)
  - [Engagements](#engagements)
  - [Utilities](#utilities)
- [Try the Examples](#try-the-examples)
- [Installation](#installation)

## Prerequisites

Before you begin, you will need the following:

1. Python 3.9+
2. Xircuits
3. HubSpot account with API access
4. HubSpot Private App access token

### Getting a HubSpot Access Token

1. Log in to your HubSpot account
2. Navigate to Settings > Integrations > Private Apps
3. Click "Create a private app"
4. Give your app a name and select the required scopes:
   - `crm.objects.contacts.read` / `crm.objects.contacts.write`
   - `crm.objects.companies.read` / `crm.objects.companies.write`
   - `crm.objects.deals.read` / `crm.objects.deals.write`
   - `crm.schemas.contacts.read` (for properties)
5. Create the app and copy the access token

## Main Xircuits Components

### Client

#### HubSpotClient
Initializes a HubSpot API client with your access token. This client is required by all other HubSpot components.

### Contacts

#### HubSpotCreateContact
Creates a new contact in HubSpot with email, name, phone, company, and custom properties.

#### HubSpotGetContact
Retrieves a contact by ID with specified properties.

#### HubSpotUpdateContact
Updates an existing contact's properties.

#### HubSpotDeleteContact
Archives (soft-deletes) a contact from HubSpot.

#### HubSpotListContacts
Lists contacts with pagination support.

#### HubSpotSearchContacts
Searches for contacts using filters and query strings.

### Companies

#### HubSpotCreateCompany
Creates a new company with name, domain, industry, and custom properties.

#### HubSpotGetCompany
Retrieves a company by ID.

#### HubSpotUpdateCompany
Updates an existing company's properties.

#### HubSpotDeleteCompany
Archives a company from HubSpot.

#### HubSpotListCompanies
Lists companies with pagination support.

#### HubSpotSearchCompanies
Searches for companies using filters.

### Deals

#### HubSpotCreateDeal
Creates a new deal with name, pipeline, stage, amount, and custom properties.

#### HubSpotGetDeal
Retrieves a deal by ID.

#### HubSpotUpdateDeal
Updates an existing deal's properties.

#### HubSpotDeleteDeal
Archives a deal from HubSpot.

#### HubSpotListDeals
Lists deals with pagination support.

#### HubSpotSearchDeals
Searches for deals using filters.

### Associations

#### HubSpotAssociateObjects
Creates associations between HubSpot objects (e.g., contact to company, deal to contact).

#### HubSpotGetAssociations
Retrieves all associations for a given object.

### Engagements

#### HubSpotCreateNote
Creates a note engagement and optionally associates it with contacts, companies, or deals.

#### HubSpotCreateTask
Creates a task with subject, body, due date, priority, and status. Can be associated with CRM objects.

### Utilities

#### HubSpotGetPipelines
Retrieves all pipelines for deals or tickets, including their stages.

#### HubSpotGetOwners
Lists all HubSpot owners (users) in the account.

#### HubSpotGetProperties
Gets all property definitions for an object type.

#### HubSpotCreateProperty
Creates a custom property for contacts, companies, deals, or other objects.

## Try the Examples

We have provided example workflows to help you get started with the HubSpot component library.

### Create Contact Example
A simple workflow that demonstrates how to:
1. Initialize the HubSpot client
2. Create a new contact
3. Retrieve the created contact

### CRM Workflow Example
A more comprehensive workflow showing:
1. Creating a company
2. Creating a contact
3. Associating the contact with the company
4. Creating a deal
5. Adding a note to the deal

## Installation

To use this component library, ensure that you have an existing [Xircuits setup](https://xircuits.io/docs/main/Installation). You can then install the HubSpot library using the [component library interface](https://xircuits.io/docs/component-library/installation#installation-using-the-xircuits-library-interface), or through the CLI using:

```bash
xircuits install hubspot
```

You can also do it manually by cloning and installing it:

```bash
# base Xircuits directory
git clone https://github.com/XpressAI/xai-hubspot xai_components/xai_hubspot
pip install -r xai_components/xai_hubspot/requirements.txt
```

## Environment Variables

You can set your HubSpot access token as an environment variable:

```bash
export HUBSPOT_ACCESS_TOKEN="your-access-token-here"
```

Then use it in your workflows with the `HubSpotClient` component.

## Filter Examples

When using search components, you can pass filters like:

```python
# Search for contacts with a specific email domain
filters = [
    {
        "propertyName": "email",
        "operator": "CONTAINS_TOKEN",
        "value": "example.com"
    }
]

# Search for deals in a specific stage
filters = [
    {
        "propertyName": "dealstage",
        "operator": "EQ",
        "value": "closedwon"
    }
]

# Search for companies by industry
filters = [
    {
        "propertyName": "industry",
        "operator": "EQ",
        "value": "TECHNOLOGY"
    }
]
```

### Available Filter Operators

- `EQ` - Equal to
- `NEQ` - Not equal to
- `LT` - Less than
- `LTE` - Less than or equal to
- `GT` - Greater than
- `GTE` - Greater than or equal to
- `CONTAINS_TOKEN` - Contains (for text fields)
- `NOT_CONTAINS_TOKEN` - Does not contain
