# Instrumentation Mode - Directory Structure

This directory contains all components, modals, and features related to Instrumentation Mode.

## Structure Requirements

All instrumentation-related code must be organized in dedicated subfolders:

- `modals/` - Help, instructions, and feature-specific modals
- `controls/` - Hook controls, plugin manager, active hooks list
- `templates/` - Hook template library components
- `plugins/` - Plugin management components
- `console/` - Real-time console output components

## Separation of Concerns

Keep Analysis Mode and Instrumentation Mode completely separate:
- Analysis Mode: `components/` (existing structure)
- Instrumentation Mode: `components/instrumentation/` (this directory)

No mixing of concerns between modes.

## Important

**Delete this file once all instrumentation features are fully implemented.**
