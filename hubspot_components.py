"""
Xircuits Component Library for HubSpot CRM Integration.

This library provides components for interacting with the HubSpot CRM API,
including operations for contacts, companies, deals, and engagements.
"""

from xai_components.base import InArg, OutArg, InCompArg, Component, xai_component
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate as ContactInput
from hubspot.crm.contacts import SimplePublicObjectInput as ContactUpdateInput
from hubspot.crm.companies import SimplePublicObjectInputForCreate as CompanyInput
from hubspot.crm.companies import SimplePublicObjectInput as CompanyUpdateInput
from hubspot.crm.deals import SimplePublicObjectInputForCreate as DealInput
from hubspot.crm.deals import SimplePublicObjectInput as DealUpdateInput
from hubspot.crm.objects.notes import SimplePublicObjectInputForCreate as NoteInput
from hubspot.crm.objects.tasks import SimplePublicObjectInputForCreate as TaskInput
import json


# ==================== CLIENT INITIALIZATION ====================

@xai_component
class HubSpotClient(Component):
    """Initialize a HubSpot API client and store it in context.

    Creates a HubSpot client instance and stores it in ctx['hubspot_client']
    for use by all other HubSpot components. This component should be used
    once at the start of a workflow.

    #### inPorts:
    - access_token: HubSpot API access token (private app token).
    """

    access_token: InCompArg[str]

    def execute(self, ctx) -> None:
        client = HubSpot(access_token=self.access_token.value)
        ctx['hubspot_client'] = client
        print("HubSpot client initialized and stored in context")


# ==================== CONTACT COMPONENTS ====================

@xai_component
class HubSpotCreateContact(Component):
    """Create a new contact in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - email: Contact email address.
    - firstname: Contact first name.
    - lastname: Contact last name.
    - phone: Contact phone number (optional).
    - company: Contact company name (optional).
    - properties: Additional properties as dict (optional).

    #### outPorts:
    - contact_id: ID of the created contact.
    - contact: Full contact object.
    """

    email: InCompArg[str]
    firstname: InArg[str]
    lastname: InArg[str]
    phone: InArg[str]
    company: InArg[str]
    properties: InArg[dict]

    contact_id: OutArg[str]
    contact: OutArg[dict]

    def execute(self, ctx) -> None:
        props = {
            "email": self.email.value
        }

        if self.firstname.value:
            props["firstname"] = self.firstname.value
        if self.lastname.value:
            props["lastname"] = self.lastname.value
        if self.phone.value:
            props["phone"] = self.phone.value
        if self.company.value:
            props["company"] = self.company.value
        if self.properties.value:
            props.update(self.properties.value)

        contact_input = ContactInput(properties=props)
        result = ctx['hubspot_client'].crm.contacts.basic_api.create(
            simple_public_object_input_for_create=contact_input
        )

        self.contact_id.value = result.id
        self.contact.value = result.to_dict()
        print(f"Created contact: {result.id}")


@xai_component
class HubSpotGetContact(Component):
    """Get a contact by ID from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - contact_id: ID of the contact to retrieve.
    - properties: List of properties to retrieve (optional).

    #### outPorts:
    - contact: Contact object as dict.
    """

    contact_id: InCompArg[str]
    properties: InArg[list]

    contact: OutArg[dict]

    def execute(self, ctx) -> None:
        props = self.properties.value if self.properties.value else [
            "email", "firstname", "lastname", "phone", "company"
        ]

        result = ctx['hubspot_client'].crm.contacts.basic_api.get_by_id(
            contact_id=self.contact_id.value,
            properties=props
        )

        self.contact.value = result.to_dict()
        print(f"Retrieved contact: {self.contact_id.value}")


@xai_component
class HubSpotUpdateContact(Component):
    """Update an existing contact in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - contact_id: ID of the contact to update.
    - properties: Properties to update as dict.

    #### outPorts:
    - contact: Updated contact object.
    """

    contact_id: InCompArg[str]
    properties: InCompArg[dict]

    contact: OutArg[dict]

    def execute(self, ctx) -> None:
        update_input = ContactUpdateInput(properties=self.properties.value)
        result = ctx['hubspot_client'].crm.contacts.basic_api.update(
            contact_id=self.contact_id.value,
            simple_public_object_input=update_input
        )

        self.contact.value = result.to_dict()
        print(f"Updated contact: {self.contact_id.value}")


@xai_component
class HubSpotDeleteContact(Component):
    """Delete a contact from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - contact_id: ID of the contact to delete.

    #### outPorts:
    - success: Boolean indicating if deletion was successful.
    """

    contact_id: InCompArg[str]

    success: OutArg[bool]

    def execute(self, ctx) -> None:
        ctx['hubspot_client'].crm.contacts.basic_api.archive(
            contact_id=self.contact_id.value
        )
        self.success.value = True
        print(f"Deleted contact: {self.contact_id.value}")


@xai_component
class HubSpotListContacts(Component):
    """List contacts from HubSpot with pagination.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - limit: Maximum number of contacts to return (default 100).
    - properties: List of properties to retrieve (optional).
    - after: Cursor for pagination (optional).

    #### outPorts:
    - contacts: List of contact objects.
    - next_page: Cursor for next page (if available).
    """

    limit: InArg[int]
    properties: InArg[list]
    after: InArg[str]

    contacts: OutArg[list]
    next_page: OutArg[str]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "email", "firstname", "lastname", "phone", "company"
        ]

        result = ctx['hubspot_client'].crm.contacts.basic_api.get_page(
            limit=limit,
            properties=props,
            after=self.after.value if self.after.value else None
        )

        self.contacts.value = [c.to_dict() for c in result.results]
        self.next_page.value = result.paging.next.after if result.paging and result.paging.next else None
        print(f"Retrieved {len(self.contacts.value)} contacts")


@xai_component
class HubSpotSearchContacts(Component):
    """Search for contacts in HubSpot using filters.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - query: Search query string (optional).
    - filters: List of filter dicts with propertyName, operator, value (optional).
    - properties: List of properties to retrieve (optional).
    - limit: Maximum results (default 100).

    #### outPorts:
    - contacts: List of matching contact objects.
    - total: Total number of matching contacts.
    """

    query: InArg[str]
    filters: InArg[list]
    properties: InArg[list]
    limit: InArg[int]

    contacts: OutArg[list]
    total: OutArg[int]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "email", "firstname", "lastname", "phone", "company"
        ]

        search_request = {
            "limit": limit,
            "properties": props
        }

        if self.query.value:
            search_request["query"] = self.query.value

        if self.filters.value:
            search_request["filterGroups"] = [{
                "filters": self.filters.value
            }]

        result = ctx['hubspot_client'].crm.contacts.search_api.do_search(
            public_object_search_request=search_request
        )

        self.contacts.value = [c.to_dict() for c in result.results]
        self.total.value = result.total
        print(f"Found {result.total} contacts matching search")


# ==================== COMPANY COMPONENTS ====================

@xai_component
class HubSpotCreateCompany(Component):
    """Create a new company in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - name: Company name.
    - domain: Company website domain (optional).
    - industry: Company industry (optional).
    - properties: Additional properties as dict (optional).

    #### outPorts:
    - company_id: ID of the created company.
    - company: Full company object.
    """

    name: InCompArg[str]
    domain: InArg[str]
    industry: InArg[str]
    properties: InArg[dict]

    company_id: OutArg[str]
    company: OutArg[dict]

    def execute(self, ctx) -> None:
        props = {
            "name": self.name.value
        }

        if self.domain.value:
            props["domain"] = self.domain.value
        if self.industry.value:
            props["industry"] = self.industry.value
        if self.properties.value:
            props.update(self.properties.value)

        company_input = CompanyInput(properties=props)
        result = ctx['hubspot_client'].crm.companies.basic_api.create(
            simple_public_object_input_for_create=company_input
        )

        self.company_id.value = result.id
        self.company.value = result.to_dict()
        print(f"Created company: {result.id}")


@xai_component
class HubSpotGetCompany(Component):
    """Get a company by ID from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - company_id: ID of the company to retrieve.
    - properties: List of properties to retrieve (optional).

    #### outPorts:
    - company: Company object as dict.
    """

    company_id: InCompArg[str]
    properties: InArg[list]

    company: OutArg[dict]

    def execute(self, ctx) -> None:
        props = self.properties.value if self.properties.value else [
            "name", "domain", "industry", "phone", "city", "state", "country"
        ]

        result = ctx['hubspot_client'].crm.companies.basic_api.get_by_id(
            company_id=self.company_id.value,
            properties=props
        )

        self.company.value = result.to_dict()
        print(f"Retrieved company: {self.company_id.value}")


@xai_component
class HubSpotUpdateCompany(Component):
    """Update an existing company in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - company_id: ID of the company to update.
    - properties: Properties to update as dict.

    #### outPorts:
    - company: Updated company object.
    """

    company_id: InCompArg[str]
    properties: InCompArg[dict]

    company: OutArg[dict]

    def execute(self, ctx) -> None:
        update_input = CompanyUpdateInput(properties=self.properties.value)
        result = ctx['hubspot_client'].crm.companies.basic_api.update(
            company_id=self.company_id.value,
            simple_public_object_input=update_input
        )

        self.company.value = result.to_dict()
        print(f"Updated company: {self.company_id.value}")


@xai_component
class HubSpotDeleteCompany(Component):
    """Delete a company from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - company_id: ID of the company to delete.

    #### outPorts:
    - success: Boolean indicating if deletion was successful.
    """

    company_id: InCompArg[str]

    success: OutArg[bool]

    def execute(self, ctx) -> None:
        ctx['hubspot_client'].crm.companies.basic_api.archive(
            company_id=self.company_id.value
        )
        self.success.value = True
        print(f"Deleted company: {self.company_id.value}")


@xai_component
class HubSpotListCompanies(Component):
    """List companies from HubSpot with pagination.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - limit: Maximum number of companies to return (default 100).
    - properties: List of properties to retrieve (optional).
    - after: Cursor for pagination (optional).

    #### outPorts:
    - companies: List of company objects.
    - next_page: Cursor for next page (if available).
    """

    limit: InArg[int]
    properties: InArg[list]
    after: InArg[str]

    companies: OutArg[list]
    next_page: OutArg[str]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "name", "domain", "industry", "phone"
        ]

        result = ctx['hubspot_client'].crm.companies.basic_api.get_page(
            limit=limit,
            properties=props,
            after=self.after.value if self.after.value else None
        )

        self.companies.value = [c.to_dict() for c in result.results]
        self.next_page.value = result.paging.next.after if result.paging and result.paging.next else None
        print(f"Retrieved {len(self.companies.value)} companies")


@xai_component
class HubSpotSearchCompanies(Component):
    """Search for companies in HubSpot using filters.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - query: Search query string (optional).
    - filters: List of filter dicts with propertyName, operator, value (optional).
    - properties: List of properties to retrieve (optional).
    - limit: Maximum results (default 100).

    #### outPorts:
    - companies: List of matching company objects.
    - total: Total number of matching companies.
    """

    query: InArg[str]
    filters: InArg[list]
    properties: InArg[list]
    limit: InArg[int]

    companies: OutArg[list]
    total: OutArg[int]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "name", "domain", "industry", "phone"
        ]

        search_request = {
            "limit": limit,
            "properties": props
        }

        if self.query.value:
            search_request["query"] = self.query.value

        if self.filters.value:
            search_request["filterGroups"] = [{
                "filters": self.filters.value
            }]

        result = ctx['hubspot_client'].crm.companies.search_api.do_search(
            public_object_search_request=search_request
        )

        self.companies.value = [c.to_dict() for c in result.results]
        self.total.value = result.total
        print(f"Found {result.total} companies matching search")


# ==================== DEAL COMPONENTS ====================

@xai_component
class HubSpotCreateDeal(Component):
    """Create a new deal in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - dealname: Name of the deal.
    - pipeline: Pipeline ID (optional, uses default if not provided).
    - dealstage: Deal stage ID (optional).
    - amount: Deal amount (optional).
    - properties: Additional properties as dict (optional).

    #### outPorts:
    - deal_id: ID of the created deal.
    - deal: Full deal object.
    """

    dealname: InCompArg[str]
    pipeline: InArg[str]
    dealstage: InArg[str]
    amount: InArg[str]
    properties: InArg[dict]

    deal_id: OutArg[str]
    deal: OutArg[dict]

    def execute(self, ctx) -> None:
        props = {
            "dealname": self.dealname.value
        }

        if self.pipeline.value:
            props["pipeline"] = self.pipeline.value
        if self.dealstage.value:
            props["dealstage"] = self.dealstage.value
        if self.amount.value:
            props["amount"] = self.amount.value
        if self.properties.value:
            props.update(self.properties.value)

        deal_input = DealInput(properties=props)
        result = ctx['hubspot_client'].crm.deals.basic_api.create(
            simple_public_object_input_for_create=deal_input
        )

        self.deal_id.value = result.id
        self.deal.value = result.to_dict()
        print(f"Created deal: {result.id}")


@xai_component
class HubSpotGetDeal(Component):
    """Get a deal by ID from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - deal_id: ID of the deal to retrieve.
    - properties: List of properties to retrieve (optional).

    #### outPorts:
    - deal: Deal object as dict.
    """

    deal_id: InCompArg[str]
    properties: InArg[list]

    deal: OutArg[dict]

    def execute(self, ctx) -> None:
        props = self.properties.value if self.properties.value else [
            "dealname", "amount", "dealstage", "pipeline", "closedate"
        ]

        result = ctx['hubspot_client'].crm.deals.basic_api.get_by_id(
            deal_id=self.deal_id.value,
            properties=props
        )

        self.deal.value = result.to_dict()
        print(f"Retrieved deal: {self.deal_id.value}")


@xai_component
class HubSpotUpdateDeal(Component):
    """Update an existing deal in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - deal_id: ID of the deal to update.
    - properties: Properties to update as dict.

    #### outPorts:
    - deal: Updated deal object.
    """

    deal_id: InCompArg[str]
    properties: InCompArg[dict]

    deal: OutArg[dict]

    def execute(self, ctx) -> None:
        update_input = DealUpdateInput(properties=self.properties.value)
        result = ctx['hubspot_client'].crm.deals.basic_api.update(
            deal_id=self.deal_id.value,
            simple_public_object_input=update_input
        )

        self.deal.value = result.to_dict()
        print(f"Updated deal: {self.deal_id.value}")


@xai_component
class HubSpotDeleteDeal(Component):
    """Delete a deal from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - deal_id: ID of the deal to delete.

    #### outPorts:
    - success: Boolean indicating if deletion was successful.
    """

    deal_id: InCompArg[str]

    success: OutArg[bool]

    def execute(self, ctx) -> None:
        ctx['hubspot_client'].crm.deals.basic_api.archive(
            deal_id=self.deal_id.value
        )
        self.success.value = True
        print(f"Deleted deal: {self.deal_id.value}")


@xai_component
class HubSpotListDeals(Component):
    """List deals from HubSpot with pagination.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - limit: Maximum number of deals to return (default 100).
    - properties: List of properties to retrieve (optional).
    - after: Cursor for pagination (optional).

    #### outPorts:
    - deals: List of deal objects.
    - next_page: Cursor for next page (if available).
    """

    limit: InArg[int]
    properties: InArg[list]
    after: InArg[str]

    deals: OutArg[list]
    next_page: OutArg[str]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "dealname", "amount", "dealstage", "pipeline", "closedate"
        ]

        result = ctx['hubspot_client'].crm.deals.basic_api.get_page(
            limit=limit,
            properties=props,
            after=self.after.value if self.after.value else None
        )

        self.deals.value = [d.to_dict() for d in result.results]
        self.next_page.value = result.paging.next.after if result.paging and result.paging.next else None
        print(f"Retrieved {len(self.deals.value)} deals")


@xai_component
class HubSpotSearchDeals(Component):
    """Search for deals in HubSpot using filters.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - query: Search query string (optional).
    - filters: List of filter dicts with propertyName, operator, value (optional).
    - properties: List of properties to retrieve (optional).
    - limit: Maximum results (default 100).

    #### outPorts:
    - deals: List of matching deal objects.
    - total: Total number of matching deals.
    """

    query: InArg[str]
    filters: InArg[list]
    properties: InArg[list]
    limit: InArg[int]

    deals: OutArg[list]
    total: OutArg[int]

    def execute(self, ctx) -> None:
        limit = self.limit.value if self.limit.value else 100
        props = self.properties.value if self.properties.value else [
            "dealname", "amount", "dealstage", "pipeline", "closedate"
        ]

        search_request = {
            "limit": limit,
            "properties": props
        }

        if self.query.value:
            search_request["query"] = self.query.value

        if self.filters.value:
            search_request["filterGroups"] = [{
                "filters": self.filters.value
            }]

        result = ctx['hubspot_client'].crm.deals.search_api.do_search(
            public_object_search_request=search_request
        )

        self.deals.value = [d.to_dict() for d in result.results]
        self.total.value = result.total
        print(f"Found {result.total} deals matching search")


# ==================== ASSOCIATION COMPONENTS ====================

@xai_component
class HubSpotAssociateObjects(Component):
    """Create an association between two HubSpot objects.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - from_object_type: Type of the source object (contacts, companies, deals).
    - from_object_id: ID of the source object.
    - to_object_type: Type of the target object (contacts, companies, deals).
    - to_object_id: ID of the target object.
    - association_type: Type of association (optional, uses default if not provided).

    #### outPorts:
    - success: Boolean indicating if association was created.
    """

    from_object_type: InCompArg[str]
    from_object_id: InCompArg[str]
    to_object_type: InCompArg[str]
    to_object_id: InCompArg[str]
    association_type: InArg[str]

    success: OutArg[bool]

    def execute(self, ctx) -> None:
        from hubspot.crm.associations.v4 import AssociationSpec

        # Default association types between common objects
        default_types = {
            ("contacts", "companies"): "contact_to_company",
            ("companies", "contacts"): "company_to_contact",
            ("deals", "contacts"): "deal_to_contact",
            ("contacts", "deals"): "contact_to_deal",
            ("deals", "companies"): "deal_to_company",
            ("companies", "deals"): "company_to_deal",
        }

        from_type = self.from_object_type.value.lower()
        to_type = self.to_object_type.value.lower()

        assoc_type = self.association_type.value if self.association_type.value else \
            default_types.get((from_type, to_type), f"{from_type}_to_{to_type}")

        ctx['hubspot_client'].crm.associations.v4.basic_api.create(
            object_type=from_type,
            object_id=self.from_object_id.value,
            to_object_type=to_type,
            to_object_id=self.to_object_id.value,
            association_spec=[AssociationSpec(
                association_category="HUBSPOT_DEFINED",
                association_type_id=self._get_association_type_id(from_type, to_type)
            )]
        )

        self.success.value = True
        print(f"Associated {from_type}/{self.from_object_id.value} to {to_type}/{self.to_object_id.value}")

    def _get_association_type_id(self, from_type: str, to_type: str) -> int:
        """Get the HubSpot association type ID for common associations."""
        type_ids = {
            ("contacts", "companies"): 1,
            ("companies", "contacts"): 2,
            ("deals", "contacts"): 3,
            ("contacts", "deals"): 4,
            ("deals", "companies"): 5,
            ("companies", "deals"): 6,
        }
        return type_ids.get((from_type, to_type), 1)


@xai_component
class HubSpotGetAssociations(Component):
    """Get associations for a HubSpot object.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - object_type: Type of the source object (contacts, companies, deals).
    - object_id: ID of the source object.
    - to_object_type: Type of associated objects to retrieve.

    #### outPorts:
    - associations: List of associated object IDs.
    """

    object_type: InCompArg[str]
    object_id: InCompArg[str]
    to_object_type: InCompArg[str]

    associations: OutArg[list]

    def execute(self, ctx) -> None:
        result = ctx['hubspot_client'].crm.associations.v4.basic_api.get_page(
            object_type=self.object_type.value.lower(),
            object_id=self.object_id.value,
            to_object_type=self.to_object_type.value.lower()
        )

        self.associations.value = [
            {"id": assoc.to_object_id, "type": [t.to_dict() for t in assoc.association_types]}
            for assoc in result.results
        ]
        print(f"Found {len(self.associations.value)} associations")


# ==================== ENGAGEMENT COMPONENTS ====================

@xai_component
class HubSpotCreateNote(Component):
    """Create a note engagement in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - body: Note body/content.
    - contact_id: ID of contact to associate note with (optional).
    - company_id: ID of company to associate note with (optional).
    - deal_id: ID of deal to associate note with (optional).

    #### outPorts:
    - note_id: ID of the created note.
    - note: Full note object.
    """

    body: InCompArg[str]
    contact_id: InArg[str]
    company_id: InArg[str]
    deal_id: InArg[str]

    note_id: OutArg[str]
    note: OutArg[dict]

    def execute(self, ctx) -> None:
        props = {
            "hs_note_body": self.body.value,
            "hs_timestamp": str(int(__import__('time').time() * 1000))
        }

        associations = []
        if self.contact_id.value:
            associations.append({
                "to": {"id": self.contact_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}]
            })
        if self.company_id.value:
            associations.append({
                "to": {"id": self.company_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 190}]
            })
        if self.deal_id.value:
            associations.append({
                "to": {"id": self.deal_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 214}]
            })

        note_input = NoteInput(properties=props, associations=associations if associations else None)
        result = ctx['hubspot_client'].crm.objects.notes.basic_api.create(
            simple_public_object_input_for_create=note_input
        )

        self.note_id.value = result.id
        self.note.value = result.to_dict()
        print(f"Created note: {result.id}")


@xai_component
class HubSpotCreateTask(Component):
    """Create a task in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - subject: Task subject/title.
    - body: Task body/description (optional).
    - due_date: Due date as ISO string (optional).
    - priority: Task priority - LOW, MEDIUM, HIGH (optional).
    - status: Task status - NOT_STARTED, IN_PROGRESS, COMPLETED (optional).
    - contact_id: ID of contact to associate task with (optional).
    - company_id: ID of company to associate task with (optional).
    - deal_id: ID of deal to associate task with (optional).

    #### outPorts:
    - task_id: ID of the created task.
    - task: Full task object.
    """

    subject: InCompArg[str]
    body: InArg[str]
    due_date: InArg[str]
    priority: InArg[str]
    status: InArg[str]
    contact_id: InArg[str]
    company_id: InArg[str]
    deal_id: InArg[str]

    task_id: OutArg[str]
    task: OutArg[dict]

    def execute(self, ctx) -> None:
        props = {
            "hs_task_subject": self.subject.value,
            "hs_task_status": self.status.value if self.status.value else "NOT_STARTED",
            "hs_timestamp": str(int(__import__('time').time() * 1000))
        }

        if self.body.value:
            props["hs_task_body"] = self.body.value
        if self.due_date.value:
            props["hs_task_due_date"] = self.due_date.value
        if self.priority.value:
            props["hs_task_priority"] = self.priority.value

        associations = []
        if self.contact_id.value:
            associations.append({
                "to": {"id": self.contact_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 204}]
            })
        if self.company_id.value:
            associations.append({
                "to": {"id": self.company_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 192}]
            })
        if self.deal_id.value:
            associations.append({
                "to": {"id": self.deal_id.value},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 216}]
            })

        task_input = TaskInput(properties=props, associations=associations if associations else None)
        result = ctx['hubspot_client'].crm.objects.tasks.basic_api.create(
            simple_public_object_input_for_create=task_input
        )

        self.task_id.value = result.id
        self.task.value = result.to_dict()
        print(f"Created task: {result.id}")


# ==================== PIPELINE COMPONENTS ====================

@xai_component
class HubSpotGetPipelines(Component):
    """Get all pipelines for an object type from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - object_type: Object type (deals or tickets).

    #### outPorts:
    - pipelines: List of pipeline objects with stages.
    """

    object_type: InArg[str]

    pipelines: OutArg[list]

    def execute(self, ctx) -> None:
        obj_type = self.object_type.value if self.object_type.value else "deals"

        result = ctx['hubspot_client'].crm.pipelines.pipelines_api.get_all(
            object_type=obj_type
        )

        self.pipelines.value = [p.to_dict() for p in result.results]
        print(f"Retrieved {len(self.pipelines.value)} pipelines for {obj_type}")


# ==================== OWNER COMPONENTS ====================

@xai_component
class HubSpotGetOwners(Component):
    """Get all owners from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - email: Filter by owner email (optional).

    #### outPorts:
    - owners: List of owner objects.
    """

    email: InArg[str]

    owners: OutArg[list]

    def execute(self, ctx) -> None:
        result = ctx['hubspot_client'].crm.owners.owners_api.get_page(
            email=self.email.value if self.email.value else None
        )

        self.owners.value = [o.to_dict() for o in result.results]
        print(f"Retrieved {len(self.owners.value)} owners")


# ==================== PROPERTY COMPONENTS ====================

@xai_component
class HubSpotGetProperties(Component):
    """Get all properties for an object type from HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - object_type: Object type (contacts, companies, deals, etc.).

    #### outPorts:
    - properties: List of property definitions.
    """

    object_type: InCompArg[str]

    properties: OutArg[list]

    def execute(self, ctx) -> None:
        result = ctx['hubspot_client'].crm.properties.core_api.get_all(
            object_type=self.object_type.value
        )

        self.properties.value = [p.to_dict() for p in result.results]
        print(f"Retrieved {len(self.properties.value)} properties for {self.object_type.value}")


@xai_component
class HubSpotCreateProperty(Component):
    """Create a custom property for an object type in HubSpot.

    Requires HubSpotClient to be executed first to initialize the client in context.

    #### inPorts:
    - object_type: Object type (contacts, companies, deals, etc.).
    - name: Internal property name.
    - label: Display label for the property.
    - property_type: Type (string, number, date, datetime, enumeration).
    - field_type: Field type (text, textarea, number, select, checkbox, etc.).
    - group_name: Property group name.
    - description: Property description (optional).
    - options: List of options for enumeration type (optional).

    #### outPorts:
    - property: Created property definition.
    """

    object_type: InCompArg[str]
    name: InCompArg[str]
    label: InCompArg[str]
    property_type: InCompArg[str]
    field_type: InCompArg[str]
    group_name: InCompArg[str]
    description: InArg[str]
    options: InArg[list]

    property: OutArg[dict]

    def execute(self, ctx) -> None:
        from hubspot.crm.properties import PropertyCreate

        property_input = PropertyCreate(
            name=self.name.value,
            label=self.label.value,
            type=self.property_type.value,
            field_type=self.field_type.value,
            group_name=self.group_name.value,
            description=self.description.value if self.description.value else "",
            options=self.options.value if self.options.value else None
        )

        result = ctx['hubspot_client'].crm.properties.core_api.create(
            object_type=self.object_type.value,
            property_create=property_input
        )

        self.property.value = result.to_dict()
        print(f"Created property: {self.name.value}")
