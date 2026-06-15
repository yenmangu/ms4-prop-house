## Responsive Form Synchronisation (HTMX Sidebar Filters)

### Initial Problem

The catalogue filter UI exists in two locations:

- Desktop sidebar
- Mobile offcanvas drawer

Both forms were configured with HTMX-powered live search.

Intermittently, filtering would appear to fail despite requests being successfully sent to the server. Search results would sometimes update only after a second user interaction, such as clicking elsewhere on the page.

This created the impression that filter state was becoming out of sync between desktop and mobile views.

### Investigation

Initial debugging focused on form synchronisation.

Network inspection revealed multiple HTMX requests being generated during filtering, suggesting that both filter forms were participating in the interaction despite only one being visible.

Additional debugging uncovered a separate template issue:

```html
id="{% if mobile %} sidebar-form-mobile {% else %} sidebar-form-desktop {% endif
%}"
```

Whitespace inside the template expression produced invalid IDs:

```html
id=" sidebar-form-mobile "
```

which prevented reliable DOM lookups and complicated debugging.

While investigating the synchronisation layer, a multi-layer architecture was developed to maintain a single filter state across desktop and mobile views.

### Design Goal

The objective was not simply:

```text
Prevent duplicate requests
```

but:

```text
Provide a single filter state regardless of viewport
```

The user should experience one coherent filtering system whether interacting with the desktop sidebar or the mobile drawer.

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

- determining the active form
- synchronising state
- enabling and disabling forms

#### Layer 2 — Synchronisation Direction

```js
syncCorrectSourceToTarget(...)
```

Determines synchronisation ownership:

```text
desktop → mobile
or
mobile → desktop
```

based on the active viewport.

#### Layer 3 — Form Orchestration

```js
syncForms(sourceForm, targetForm);
```

Responsible for:

- iterating controls
- locating matching controls
- delegating synchronisation behaviour

#### Layer 4 — Control Matching

```js
getMatchingControl(...)
```

Handles control lookup rules:

```text
checkbox/radio → name + value
other controls → name
```

#### Layer 5 — Control Behaviour

```js
syncValueControl(...)
syncCheckedControl(...)
```

Provides specialised handling for:

```text
.value
.checked
```

state.

### Root Cause

The synchronisation architecture was ultimately not the cause of the bug.

The actual issue was an HTMX trigger configuration:

```html
hx-trigger="keyup changed delay:300ms from:input, change"
```

The `from:input` modifier broadened event handling beyond the current form, allowing multiple filter forms to react to the same input events.

As a result:

- both filter forms could issue requests
- stale form state could overwrite valid results
- responses appeared inconsistent despite the server returning correct data

Removing the modifier resolved the issue:

```html
hx-trigger="keyup changed delay:300ms, change"
```

This restricted event handling to controls within the form itself and eliminated the competing requests.

### Outcome

The final implementation provides:

- a single source of truth for filter state
- consistent desktop and mobile behaviour
- no duplicate HTMX requests
- no URL flicker
- support for future filter controls
- clear separation of responsibilities within the synchronisation layer

### Key Lesson

The most valuable insight from this investigation was that the visible symptom and the root cause were not the same problem.
The application genuinely benefited from a robust synchronisation architecture, but the bug itself originated from an overly broad HTMX event trigger.
The debugging process reinforced the importance of validating assumptions at each layer of abstraction before attributing issues to higher-level architectural concerns.
