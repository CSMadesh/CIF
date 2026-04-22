# IXOVA Apple Design System

## Color Tokens

### Primary Colors
- `--apple-blue: #007AFF` — Primary actions, links, highlights
- `--apple-green: #34C759` — Success states, positive actions
- `--apple-indigo: #5856D6` — Secondary highlights
- `--apple-orange: #FF9500` — Warnings, premium features
- `--apple-pink: #FF2D55` — Trending, urgent items
- `--apple-purple: #AF52DE` — Categories, tags
- `--apple-red: #FF3B30` — Errors, destructive actions
- `--apple-teal: #5AC8FA` — Info states
- `--apple-yellow: #FFCC00` — Highlights, notifications

### Grayscale
- `--apple-black: #000000`
- `--apple-dark-gray: #1C1C1E`
- `--apple-gray: #8E8E93`
- `--apple-light-gray: #C7C7CC`
- `--apple-extra-light-gray: #F2F2F7`
- `--apple-white: #FFFFFF`

### Semantic Tokens (Auto-switch Light/Dark)
- `--bg` — Primary background
- `--bg-2` — Secondary background (cards, sidebar hover)
- `--bg-3` — Tertiary background
- `--text` — Primary text
- `--text-2` — Secondary text
- `--text-3` — Tertiary text (labels, metadata)
- `--border` — Borders and dividers
- `--shadow` — Drop shadows
- `--overlay` — Hover overlays

## Light Mode (Default)
- Background: White (#FFFFFF) / Light Gray (#F2F2F7)
- Text: Black (#000000) / Dark Gray (#3C3C43)
- Border: #D1D1D6

## Dark Mode (Auto-detected)
- Background: Black (#000000) / Dark Gray (#1C1C1E, #2C2C2E)
- Text: White (#FFFFFF) / Light (#EBEBF5)
- Border: #38383A

## Usage Guidelines

### Buttons
- **Primary**: Blue background, white text
- **Secondary**: Light background, border, primary text
- **Danger**: Red tint background, red text
- **Ghost**: Transparent, blue text

### Badges
- Use primary colors with 12% opacity backgrounds
- Examples: `badge-blue`, `badge-green`, `badge-orange`, `badge-purple`

### Status Indicators
- Active/Success: Green
- Inactive/Error: Red
- Warning: Orange
- Info: Blue

### Typography
- Headings: 700 weight, tight letter-spacing
- Body: 500 weight
- Labels: 600 weight, uppercase, 11px

### Spacing
- Card padding: 24px
- Grid gap: 16px
- Button padding: 9px 18px (standard), 6px 12px (small)

### Border Radius
- Cards: 14px (`--radius`)
- Buttons/Inputs: 10px (`--radius-sm`)
- Badges: 20px (pill shape)

### Transitions
- Duration: 0.25s
- Easing: `cubic-bezier(0.4, 0, 0.2, 1)`

## Component Classes

### Layout
- `.main` — Main content area (with sidebar offset)
- `.topbar` — Page header with title and actions
- `.stats-grid` — 4-column stats cards
- `.cards-grid` — 3-column opportunity cards
- `.two-col` / `.three-col` — Grid layouts

### Cards
- `.card` — Standard card container
- `.stat-card` — Stat display card
- `.opp-card` — Opportunity card

### Forms
- `.form-group` — Form field wrapper
- `.form-label` — Field label
- `.form-control` — Input/textarea/select

### Tables
- `.sa-table` — Sub-admin table styling

### Utilities
- `.fade-up` — Fade-up animation
- `.fade-up-1` through `.fade-up-6` — Staggered delays
