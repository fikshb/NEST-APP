# **PRD v8.1 – NestApp & ClawdBot**

**Serviced Apartment Management System**  
_(Unified UX, Backend, Governance & Visualization)_

---

## 0. Document Purpose

This **PRD v8.1** is the **single source of truth**.

It covers:

- UI/UX & Frontend behavior
    
- Backend contract & rules
    
- Governance, audit, and compliance
    
- WhatsApp PA (ClawdBot) behavior
    
- Dashboard visualization (donut charts)
    

All previous PRD versions are **superseded**.

---

## 1. Product Overview

**Product Name:** NestApp  
**Property / Brand:** NEST – Serviced Apartment  
**Language:** English only (UI, documents, bot)  
**Primary User:** Operational Admin (single user)  
**Interaction Channels:**

- Web Application (NestApp)
    
- WhatsApp Personal Assistant (ClawdBot via OpenClaw)
    

**Product Objective:**  
Provide a **simple, guided operational system** for serviced apartment management, while enforcing **strict document discipline, auditability, and governance** behind the scenes.

---

## 2. User, Interfaces, and Actors

### 2.1 User

- **Admin**
    
    - Single user
        
    - Full authority
        
    - No roles
        
    - No RBAC
        
    - No permission matrix
        

---

### 2.2 Admin Interfaces

Admin may operate via:

1. **NestApp Web UI**
    
2. **ClawdBot (WhatsApp Personal Assistant)**
    

Both interfaces:

- Have equal authority
    
- Operate on the same rules
    
- Are fully auditable
    
- Are interchangeable at any time
    

---

### 2.3 System Component

**ClawdBot**

- Not a user
    
- Acts _on behalf of Admin_
    
- Executes actions via secure service token
    
- Channel: WhatsApp
    
- Executor: System
    
- Decision logic enforced strictly by NestApp
    

---

### 2.4 External Actors

- Tenant / Lessee
    
- Finance Holding Company
    

External actors **never log in** to NestApp.

---

## 3. Core Design Principles (LOCKED)

1. NestApp is the **single source of truth**
    
2. **Document-driven journey** (no document → no progress)
    
3. English only
    
4. One core object: **Deal**
    
5. Journey-based UX, not feature-based
    
6. Bot cannot bypass rules
    
7. Finance is external & admin-managed
    
8. Documents are immutable & versioned
    
9. All actions are auditable
    
10. UX is simple; rules are strict
    

---

## 4. Navigation & UX Structure

### 4.1 Dashboard (Landing Page)

The dashboard is the **default landing page**.

#### 4.1.1 Operational Summary (Primary)

Displayed as cards:

- Deals in Progress
    
- Deals Blocked (with reason)
    
- Deals Awaiting Action
    
- Completed Deals
    

Clicking any card opens the **Deal list filtered accordingly**.

---

#### 4.1.2 Occupancy & Status Visualization (NEW)

Dashboard may display **read-only charts**:

**A. Unit Occupancy Donut Chart**

- Available
    
- Reserved
    
- Occupied
    

**B. Deal Status Donut Chart (Optional)**

- In Progress
    
- Waiting Invoice
    
- Completed
    

Rules:

- Read-only
    
- Non-clickable
    
- No drill-down
    
- No analytics depth
    
- Informational only
    

---

### 4.2 Side Menu (Persistent, Minimal)

`Dashboard Deals Tenants Units (Rooms) Document Library Settings`

**Rule:**  
All operational actions must happen **inside a Deal**.  
Side menu is for **setup and maintenance only**.

---

## 5. Core Object Model

### Deal (Single Core Object)

All workflows revolve around **Deal**.

Supported deal types:

- Daily
    
- Monthly
    
- 6 Months
    
- 12 Months
    

System automatically determines:

- Required documents
    
- Journey steps
    
- Blocking rules
    

Admin never manages internal states.

---

## 6. Deal Journeys (User-Facing)

### 6.1 Daily Stay Journey

1. Select Unit
    
2. Generate Booking Confirmation
    
3. Generate Official Confirmation Letter
    
4. Request Invoice
    
5. Upload Invoice
    
6. Generate Unit Handover Certificate
    
7. Deal Closed
    

---

### 6.2 Monthly / 6 / 12 Months Journey

1. Select Unit
    
2. Generate Offer (LOO Draft)
    
3. Finalize Offer (LOO Final)
    
4. Generate Lease Agreement
    
5. Generate Official Confirmation Letter
    
6. Request Invoice
    
7. Upload Invoice
    
8. Generate Move-in Confirmation
    
9. Generate Unit Handover Certificate
    
10. Deal Closed
    

Each step:

- Unlocks sequentially
    
- Is blocked if required documents are missing
    

---

## 7. Deal Detail Page (Primary Work Screen)

Vertical, journey-based layout:

1. Tenant & Unit Summary
    
2. Journey Checklist
    
3. Current Step Highlight
    
4. One Primary Action Button
    

Blocked example:

> “Action required: Upload Invoice to continue.”

No secondary actions are visible.

---

## 8. Document Management (HTML → PDF)

### 8.1 System-Generated Documents

All documents:

- Written in English
    
- Formal business letter style
    
- Beautified layout
    
- NEST logo included
    
- Company e-signature image auto-applied
    
- Generated as HTML
    
- Previewable
    
- Exportable as PDF
    
- Immutable & versioned
    

**Generated documents:**

- Booking Confirmation
    
- Letter of Offer – Draft
    
- Letter of Offer – Final
    
- Lease Agreement
    
- Official Confirmation Letter
    
- Move-in Confirmation
    
- Unit Handover Certificate
    

---

### 8.2 Document Rules (Backend)

- Documents cannot be deleted
    
- Revisions generate new versions
    
- Old versions are read-only
    
- Bot always sends the latest version
    

---

## 9. Static Documents – Document Library

### Scope

- Catalog (PDF)
    
- Pricelist (PDF)
    

Rules:

- Files stored in file storage
    
- Metadata stored in DB
    
- Versioned
    
- One active version per type
    

Admin UI shows only:

- Active Catalog
    
- Active Pricelist
    

---

## 10. Tenants Module

Purpose:

- Store tenant information
    
- Reuse tenant data
    
- View tenant history
    

Fields:

- Name
    
- Phone
    
- Email
    
- Company (optional)
    
- Notes
    

No CRM complexity.

---

## 11. Units (Rooms) Module

Purpose:

- Manage inventory
    

Fields:

- Unit number
    
- Unit type
    
- Status (Available / Reserved / Occupied)
    
- Default pricing (daily, monthly, 6m, 12m)
    
- Notes
    

Unit reservation is enforced automatically by Deal status.

---

## 12. Finance Handling (External & Admin-Managed)

### Invoice Request

- Admin clicks **Request Invoice**
    
- System sends auto-generated email to Finance
    
- Deal status → Invoice Requested
    

### Invoice & Receipt Upload

- Finance sends files via email
    
- **Admin uploads files**
    
- Journey remains locked until upload is completed
    

NestApp does **not** generate invoices or receipts.

---

## 13. E-Signature (Company-Side Only)

- Signature is an uploaded image
    
- Stored securely
    
- Automatically embedded in required documents
    
- Logged with timestamp & version
    

No external e-sign provider in Phase 1.

---

## 14. Deal Cancellation & Exceptions

- Only Admin can cancel a deal
    
- Cancellation reason is mandatory
    
- Deal becomes read-only
    
- Unit availability released
    
- Fully logged
    

**Emergency Override**

- Web UI only
    
- Admin only
    
- Mandatory reason
    
- Fully auditable
    
- Not accessible by ClawdBot
    

---

## 15. ClawdBot – WhatsApp Personal Assistant

Capabilities:

- Create and update deals
    
- Trigger document generation
    
- Send generated or uploaded documents
    
- Send active catalog & pricelist
    
- Report blocked steps
    

Restrictions:

- Cannot bypass journey
    
- Cannot override documents
    
- Cannot generate finance documents
    

Audit log:

- Actor: Admin
    
- Channel: WhatsApp
    
- Executor: ClawdBot
    

---

## 16. Settings (Simple View)

Visible:

- Company information
    
- Logo
    
- Authorized signatory name & title
    
- Signature image
    
- Finance email
    
- Bot WhatsApp number
    

Advanced configuration is hidden.

---

## 17. Audit, Compliance & Governance

System logs:

- All document generations
    
- All uploads
    
- All status transitions
    
- All overrides
    
- All cancellations
    

Exports:

- Deals (CSV)
    
- Documents per deal (ZIP)
    

System is audit-ready by default.

---

## 18. Error & Blocking Communication

Admin never sees:

- Error codes
    
- Technical validation messages
    

System uses plain language:

- “Please complete the previous step.”
    
- “This action is not available yet.”
    

---

## 19. Performance & Reliability

- Dashboard charts are read-only
    
- Aggregation queries are lightweight
    
- No real-time requirement
    
- System remains usable if charts fail
    

---

## 20. Final Product Positioning

- Simple UX for Admin: **Yes**
    
- Informative dashboard: **Yes**
    
- Strong backend governance: **Yes**
    
- Audit & compliance ready: **Yes**
    
- Over-engineered UX: **No**
    

**Simple on the surface. Strict underneath.**

---

## 21. Final Lock Statement

This **PRD v8.1** is:

- Final
    
- Unified
    
- Production-ready
    
- Free of ambiguity