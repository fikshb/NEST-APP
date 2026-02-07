# NestApp — User Manual

**Serviced Apartment Management System**

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard](#2-dashboard)
3. [Deals](#3-deals)
4. [Tenants](#4-tenants)
5. [Units](#5-units)
6. [Document Library](#6-document-library)
7. [Settings](#7-settings)
8. [Audit Logs](#8-audit-logs)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Getting Started

### 1.1 Login

1. Open the application at **http://localhost:3000**
2. You will be redirected to the login page
3. Enter your **username** and **password** (provided by your system administrator)
4. Click **Login**
5. You will be taken to the Dashboard

Your session lasts 24 hours. After that, you will need to log in again.

### 1.2 Logout

1. In the left sidebar, click the **Logout** button at the bottom
2. You will be returned to the login page

### 1.3 Navigation

The left sidebar provides access to all sections:

| Menu Item        | Description                              |
|------------------|------------------------------------------|
| Dashboard        | Overview of deals, occupancy, and status |
| Deals            | Create and manage deals                  |
| Tenants          | Manage tenant information                |
| Units            | Manage apartment units and pricing       |
| Document Library | Upload and manage catalog and pricelist  |
| Settings         | Company info, logo, signature, finance   |

---

## 2. Dashboard

The Dashboard is your home screen. It shows a quick overview of your operations.

### 2.1 Summary Cards

Four cards at the top show:

- **Deals in Progress** — Active deals being worked on
- **Blocked** — Deals that need attention
- **Awaiting Action** — Deals waiting for your next step
- **Completed** — Successfully closed deals

Click any card to jump to the Deals list filtered by that status.

### 2.2 Charts

Two donut charts provide visual summaries:

- **Unit Occupancy** — How many units are Available, Reserved, or Occupied
- **Deal Status** — Distribution of deal statuses

These charts are informational only and cannot be clicked.

### 2.3 Active Deals

Below the charts is a list of deals currently in progress. Click any deal to open its detail page.

---

## 3. Deals

Deals are the core of NestApp. Every booking, lease, or agreement is tracked as a Deal.

### 3.1 Deal Types

| Type         | Journey Steps | Documents Generated                                    |
|--------------|---------------|-------------------------------------------------------|
| Daily        | 5 steps       | Booking Confirmation                                   |
| Monthly      | 10 steps      | LOO Draft, LOO Final, Lease Agreement, Official Confirmation, Move-in Confirmation, Unit Handover |
| 6 Months     | 10 steps      | Same as Monthly                                        |
| 12 Months    | 10 steps      | Same as Monthly                                        |

### 3.2 Creating a Deal

1. Go to **Deals** from the sidebar
2. Click **New Deal**
3. Fill in the form:
   - **Tenant** — Select an existing tenant from the dropdown
   - **Unit** — Select an available unit (only available units are shown)
   - **Term Type** — Choose Daily, Monthly, 6 Months, or 12 Months
   - **Start Date** — When the stay begins
   - **End Date** — When the stay ends (optional for monthly+)
4. Click **Create Deal**
5. The price is automatically set from the unit's pricing for the selected term type
6. The unit status changes to **Reserved**
7. You are taken to the Deal Detail page

### 3.3 Deal Detail Page

The Deal Detail page is your primary work screen. It contains:

#### Tenant & Unit Summary
Shows the tenant's name, email, phone, and the unit details including list price and agreed price.

#### Journey Progress
A vertical checklist showing all steps in the deal's journey:
- **Green checkmark** — Step completed
- **Blue circle** — Current step (requires your action)
- **Grey circle** — Future step (locked)

#### Action Button
At the bottom of the journey checklist, there is always exactly **one action button** for the current step. The button label changes based on the step:
- "Generate Booking Confirmation"
- "Generate Offer (LOO Draft)"
- "Finalize Offer (LOO Final)"
- "Generate Lease Agreement"
- "Generate Official Confirmation"
- "Request Invoice"
- "Upload Invoice"
- "Generate Move-in Confirmation"
- "Generate Handover Certificate"
- "Close Deal"

#### Documents Panel
On the right side, all generated documents are listed with:
- Document type and version number
- **Preview** link — Opens the HTML version in a new tab
- **Download PDF** link — Downloads the PDF version

### 3.4 Price Negotiation

You can set a negotiated price that differs from the unit's list price:

**For Daily deals:**
- At the **Generate Booking Confirmation** step, a price input field appears
- Enter the negotiated price (or leave empty to use the list price)
- The price is automatically saved when you click "Generate Booking Confirmation"

**For Monthly / 6M / 12M deals:**
- At the **Finalize Offer (LOO Final)** step, a price input field appears
- Enter the negotiated price (or leave empty to use the list price)
- You can click "Set Price" to save it first, or it will be auto-saved when you generate the document

### 3.5 Move-in Details (Monthly / 6M / 12M only)

At the **Generate Move-in Confirmation** step:

1. Enter the **Move-in Date**
2. Optionally list **Items to Move In** (one per line)
3. Click **Save Move-in Details**
4. Then click **Generate Move-in Confirmation** to create the document

### 3.6 Invoice Flow

The invoice process involves two steps:

**Step 1 — Request Invoice:**
1. Click **Request Invoice**
2. An email is automatically sent to the finance department
3. The deal status changes to "Invoice Requested"

**Step 2 — Upload Invoice:**
1. Wait for finance to send the invoice via email
2. Click **Upload Invoice** and select the invoice file (PDF, JPG, or PNG)
3. The file is uploaded and the deal advances to the next step

### 3.7 Closing a Deal

When all steps are completed:
1. The journey reaches the **Deal Closed** step
2. Click **Close Deal**
3. The deal status changes to **Completed**
4. The unit status changes to **Occupied**

### 3.8 Cancelling a Deal

You can cancel a deal at any point (unless already completed or cancelled):

1. Click the **Cancel Deal** button (top right, red text)
2. Enter a **reason for cancellation** (required)
3. Click **Confirm Cancellation**
4. The deal becomes read-only
5. The unit is released back to **Available**

### 3.9 Emergency Override

If you need to skip or jump to a specific step (use with caution):

1. Click **Emergency Override** (top right)
2. Select the **Target Step** from the dropdown
3. Enter a **reason** (required)
4. Click **Apply Override**
5. The action is fully logged in the audit trail

Emergency override is only available on the Web UI (not via WhatsApp bot).

---

## 4. Tenants

The Tenants section stores information about your guests and lessees.

### 4.1 Viewing Tenants

1. Go to **Tenants** from the sidebar
2. Use the **search box** to find tenants by name, email, or phone
3. Click a tenant to see their details

### 4.2 Creating a Tenant

1. Click **Add Tenant**
2. Fill in the form:
   - **Full Name** (required)
   - **Phone** (required)
   - **Email** (required)
   - **Company Name** (optional)
   - **Notes** (optional)
3. Click **Save**

### 4.3 Editing a Tenant

1. Click the **pencil icon** next to the tenant
2. Update the information
3. Click **Save**

### 4.4 Archiving a Tenant

Tenants cannot be deleted (to preserve deal history). Instead, you can archive them:

1. Edit the tenant
2. Check the **Archived** checkbox
3. Click **Save**

Archived tenants are hidden from the default list but can still be viewed with the filter.

---

## 5. Units

The Units section manages your apartment inventory.

### 5.1 Viewing Units

1. Go to **Units** from the sidebar
2. Units are displayed as cards showing:
   - Unit code (e.g., 101, 102)
   - Unit type (e.g., Standard)
   - Status badge (Available, Reserved, Occupied)
   - Configured prices

### 5.2 Creating a Unit

1. Click **Add Unit**
2. Fill in the form:
   - **Unit Code** (required, must be unique)
   - **Unit Type** (e.g., Standard, Deluxe)
   - **Daily Price** (optional)
   - **Monthly Price** (optional)
   - **6-Month Price** (optional)
   - **12-Month Price** (optional)
3. Click **Save**

You only need to set prices for the term types you offer. For example, if a unit is only available for monthly stays, you only need to set the monthly price.

### 5.3 Editing a Unit

1. Click the **pencil icon** on the unit card
2. Update the information and pricing
3. Click **Save**

### 5.4 Unit Status

Unit status is managed automatically by the system:

| Status      | Meaning                                     |
|-------------|---------------------------------------------|
| Available   | Ready for new deals                         |
| Reserved    | A deal has been created for this unit       |
| Occupied    | The deal is completed, tenant has moved in  |

- Creating a deal changes the unit to **Reserved**
- Closing a deal changes the unit to **Occupied**
- Cancelling a deal releases the unit back to **Available**

---

## 6. Document Library

The Document Library manages two reference documents: the Unit Catalog and the Pricelist.

### 6.1 Uploading a New Version

1. Go to **Document Library** from the sidebar
2. Click **Upload New Version** on either the Catalog or Pricelist card
3. Select a **PDF file**
4. The new version becomes the active version immediately

### 6.2 Viewing Documents

- Click **View Active PDF** to open the current version in a new tab
- Version history is shown below with upload dates

These documents can be sent to tenants via the WhatsApp bot (ClawdBot) on request.

---

## 7. Settings

The Settings page manages your company information used in generated documents.

### 7.1 Company Information

| Field             | Description                                        |
|-------------------|----------------------------------------------------|
| Company Legal Name | Full legal entity name (shown on documents)       |
| Company Address    | Physical address (shown on documents)             |
| Signatory Name     | Name of the authorized signatory                  |
| Signatory Title    | Title/position of the signatory                   |
| Finance Email      | Email address where invoice requests are sent     |
| Bot WhatsApp No.   | WhatsApp number for ClawdBot integration          |

Click **Save Settings** after making changes.

### 7.2 Company Logo

1. Click **Upload Logo** in the Logo section
2. Select an image file (PNG, JPG, or WEBP)
3. The logo is automatically embedded in all generated documents

### 7.3 Signature Image

1. Click **Upload Signature** in the Signature section
2. Select an image file containing the authorized signature
3. The signature is automatically embedded in all generated documents that require it

---

## 8. Audit Logs

NestApp logs every action for compliance and accountability.

### 8.1 Viewing Audit Logs

1. The audit log is accessible from the Deal Detail page or via API
2. Each log entry shows:
   - **Action** — What happened (e.g., CREATE_DEAL, GENERATE_DOCUMENT)
   - **Summary** — Human-readable description
   - **Channel** — WEB or WHATSAPP
   - **Executor** — WEB (you) or CLAWDBOT (bot)
   - **Timestamp** — When it happened

### 8.2 Exporting Audit Logs

Audit logs can be exported as CSV for external analysis:
- Use the **Export** function to download a CSV file
- Filter by deal to export logs for a specific deal

---

## 9. Troubleshooting

### "Not authenticated" error when previewing documents

This should not happen under normal use. If it does:
1. Log out and log back in
2. Try the Preview/Download link again
3. Your session may have expired (tokens last 24 hours)

### Cannot create a deal — "Unit not available"

The selected unit is already Reserved or Occupied by another deal. Either:
- Choose a different unit
- Cancel the existing deal on that unit first

### Cannot progress a deal — "This action is not available yet"

You need to complete the current step before moving to the next. Check the Journey Progress checklist to see which step needs attention.

### Document shows wrong price

Make sure you set the negotiated price **before** clicking the Generate button. The price input appears at:
- **Booking Confirmation** step (daily deals)
- **Finalize LOO** step (monthly/6M/12M deals)

If you already generated the document, you can use **Emergency Override** to go back to the pricing step, set the correct price, and regenerate.

### Login fails

- Check that you are using the correct username and password
- Credentials are set in the environment variables — contact your system administrator
- The default username is `adminnest`
