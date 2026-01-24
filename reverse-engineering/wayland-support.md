# Wayland Support Implementation Notes

## Current Status

### What Works Now:
- **X11**: Full support via `mss` library ✅
- **XWayland**: Full support via `mss` library ✅
- **Native Wayland**: ❌ Requires portal-based capture

## Wayland Challenge

Wayland's security model prevents direct screen capture. Applications must use:
- **xdg-desktop-portal** - Screen capture portal API
- **PipeWire** - Media streaming framework

## Implementation Plan

### Option 1: Detect and Use Portals (Recommended)
```python
# Detect session type
if os.environ.get('WAYLAND_DISPLAY'):
    # Use portal-based capture
    use_wayland_portal_capture()
else:
    # Use mss for X11
    use_mss_capture()
```

### Option 2: python-xdg-desktop-portal
Library that wraps portal APIs for Python.

### Option 3: Fall back to X11 capture via XWayland
- Request access via portal first
- If denied, show error with instructions
- Most apps run under XWayland anyway on Wayland

## Testing Requirements

Need to test on:
1. Pure X11 session
2. XWayland under Wayland compositor
3. Native Wayland app (GTK4/Qt6 Wayland)

## Dependencies for Wayland

Additional packages needed:
```
python-dbus (for D-Bus communication)
PyGObject (for portal interaction)
```

Or use subprocess to call portal utilities:
```bash
grim # Wayland screenshot tool
slurp # Region selection for Wayland
```

## Decision

For MVP:
1. Test with `mss` on X11/XWayland (covers 90% of cases)
2. Add portal support in next iteration
3. Document Wayland limitations in README

For full support:
- Add portal-based capture engine
- Auto-detect session type
- Seamlessly switch between methods
