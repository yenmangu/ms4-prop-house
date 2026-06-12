## Responsive Form Synchronisation (HTMX Sidebar Filters)

### Initial Problem

The catalogue filter UI exists in two places:

- Desktop sidebar
- Mobile offcanvas drawer

Both forms were configured with HTMX live search.

When typing into the desktop search box, two requests were being generated:

```text
GET /?q=oil
GET /?q=
```

This caused:

- URL flickering (`?q=oil` → `?q=`)
- Search results appearing not to update
- Race conditions between desktop and mobile forms

### Investigation

Request headers revealed:

```text
HX-Trigger: sidebar-form-desktop
HX-Trigger: sidebar-form-mobile
```

Both forms were active simultaneously despite only one being visible.

Further debugging exposed an unrelated template bug:

```html
id="{% if mobile %} sidebar-form-mobile {% else %} sidebar-form-desktop {% endif
%}"
```

Whitespace inside the template expression resulted in invalid IDs:

```html
id=" sidebar-form-mobile "
```

which prevented DOM queries from locating the forms correctly.

### Design Goal

The desired outcome was not merely:

```text
"Prevent duplicate HTMX requests"
```

but:

```text
"Ensure the user experiences a single filter state regardless of viewport"
```

This became the primary architectural concern.

### Pyramid of Concerns

```text
User Experience
    ↓
Single filter state
    ↓
Form synchronisation
    ↓
Source/target ownership
    ↓
Control matching
    ↓
Control type handling
```

### Final Architecture

#### Layer 1 — Sidebar State

```js
syncSidebarForms(mobileIsActive);
```

Responsible for:

- determining active form
- synchronising state
- enabling/disabling forms

#### Layer 2 — Synchronisation Direction

```js
syncCorrectSourceToTarget(...)
```

Determines:

```text
desktop → mobile
or
mobile → desktop
```

based on active viewport state.

#### Layer 3 — Form Orchestration

```js
syncForms(sourceForm, targetForm);
```

Responsible for:

- iterating controls
- locating matching controls
- delegating sync behaviour

#### Layer 4 — Matching

```js
getMatchingControl(...)
```

Handles:

```text
checkbox/radio -> name + value
other controls -> name
```

### Layer 5 — Control Behaviour

```js
syncValueControl(...)
syncCheckedControl(...)
```

Separate handling for:

```text
.value
.checked
```

state.

### Outcome

The final solution provides:

- Single source of truth for filter state
- No duplicate HTMX requests
- No URL flicker
- Consistent desktop/mobile behaviour
- Automatic support for future form controls
- Minimal coupling to HTMX

### Key Lesson

The most valuable insight was that the bug was not really an HTMX problem.

The real problem was maintaining a single conceptual filter state across multiple responsive UIs.

Once the problem was reframed at that level, the implementation naturally emerged as a set of increasingly focused layers with clear responsibilities.
