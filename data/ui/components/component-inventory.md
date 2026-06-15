# Component Inventory

管理画面・ダッシュボード・業務システムで標準利用するコンポーネント一覧。

## Layout

| Component | Purpose | Mobile Behavior |
|---|---|---|
| App Shell | Header + Sidebar + Main layout | Sidebar becomes drawer |
| Header Bar | Page title, actions, user menu | Title wraps, actions move below |
| Sidebar Navigation | Primary navigation | Off-canvas drawer |
| Breadcrumb | Current location | Horizontal scroll or hidden middle |
| Section Header | Section title and actions | Actions stack vertically |
| Two Column Layout | Detail + side panel | Single column |
| Split Pane | List + detail | Detail moves below or separate page |

## Data Display

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Data Table | List records | Horizontal scroll or card list |
| Sortable Table Header | Sort by column | Keep visible for scroll table |
| Row Actions | Edit/delete/detail | Moves into kebab menu |
| Status Badge | Status display | Inline badge |
| KPI Card | Dashboard metrics | 1 column grid |
| Chart Card | Graph container | Full width |
| Description List | Detail fields | Stacked |
| Timeline | History/audit log | Full width vertical |
| Empty State | No data guidance | Centered compact |

## Inputs / Forms

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Text Input | Basic input | Full width |
| Textarea | Long text | Full width |
| Select | Choice | Full width |
| Checkbox Group | Multiple select | Stacked |
| Radio Group | Single select | Stacked |
| Date Input | Date | Full width |
| File Upload | Upload | Full width |
| Search Box | Keyword search | Full width |
| Filter Panel | Advanced search | Collapsible |
| Form Error Summary | Top error summary | Full width |
| Inline Error | Field-level error | Under field |

## Actions

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Button | Primary/secondary/destructive action | Full width optional |
| Button Group | Multiple actions | Stack or wrap |
| Icon Button | Compact action | Minimum tap size |
| Bulk Action Bar | Batch operations | Sticky bottom or stacked |
| Floating Action Button | Main mobile action | Optional for mobile only |

## Feedback

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Alert | Page-level message | Full width |
| Toast | Temporary message | Bottom centered |
| Loading Spinner | Wait state | Centered |
| Skeleton | Loading placeholder | Matches layout |
| Progress Indicator | Step/process state | Horizontal scroll or vertical |
| Confirmation Dialog | Destructive confirmation | Near full width |

## Navigation / Workflow

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Pagination | Page navigation | Previous/Next + current page |
| Tabs | Section switching | Horizontal scroll |
| Stepper | Multi-step input | Vertical compact |
| Drawer | Side panel | Full-height overlay |
| Modal | Dialog/edit form | Full-width sheet style |

## Business Components

| Component | Purpose | Mobile Behavior |
|---|---|---|
| Mail Editor | Subject/body/template editing | Full width, toolbar wraps |
| Comment Box | Internal note | Full width |
| Approval Flow | Request/approve/reject | Vertical timeline |
| Audit Log | Operation history | Vertical list |
| CSV Import | File import + mapping | Stepper |
| CSV Export | Export options | Modal or panel |
| Attachment List | Files | Stacked list |
| User/Role Selector | Permission assignment | Search + chips |

## Mandatory States

All components must define the following where applicable.

- default
- hover
- focus
- active
- disabled
- loading
- error
- success
- empty
- readonly
