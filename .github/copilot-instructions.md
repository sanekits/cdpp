# Copilot Instructions for cdpp

## Project Overview

cdpp is a shell extension that enhances the Bash `cd` command with additional behaviors and features. It provides wrapper functionality around the standard directory navigation command to add convenience features for shell users.

## Architecture

- **Shell Integration**: This project integrates with the Bash by wrapping or extending the `cd` command
- **Script-based**: Implementation is primarily shell scripts that need to be sourced or integrated into the shell environment
- **Backward Compatibility**: Maintain compatibility with standard `cd` behavior while adding enhancements
- **Bash only**:  No attempt is made to support other shells

## Modernization Guidelines

### Code Quality
- Use modern shell scripting best practices (shellcheck compliance)
- Add proper error handling with meaningful error messages
- Use `[[` instead of `[` for conditionals in bash
- Quote variables to prevent word splitting: `"$var"` not `$var`
- Use `$(command)` instead of backticks
- Put logic into functions in shell scripts

### Documentation
- Maintain clear README with installation and usage instructions
- Document all functions with comments explaining purpose and parameters
- Include examples for all features

### Testing
- Add shellcheck validation to catch common issues
- Consider adding bats (Bash Automated Testing System) for unit tests


## Common Pitfalls to Avoid

- **Path Handling**: Always handle paths with spaces and special characters properly
- **Environment Variables**: Be careful not to pollute the global namespace needlessly
- **Side Effects**: Ensure the wrapper doesn't break existing `cd` functionality

## Code Patterns to Follow

### Function Definitions
```bash
function_name() {
    local var_name="$1"
    # Implementation
}
```

### Error Checking
```bash
_cdpp_err() {
  echo "ERROR: $*" >&2
  return 1
}
if [[ ! -d "$directory" ]]; then
    return _cdpp_err "Error: Directory does not exist: $directory" >&2
fi
```

### Safe Variable Usage
```bash
# Always quote variables
cd "$target_dir" || return 1
```

## Maintenance Priorities

1. **Shellcheck Clean**: All scripts should pass shellcheck with no warnings
3. **Performance**: Keep the overhead minimal since `cd` is frequently used
4. **Documentation**: Keep docs in sync with code changes

## Feature Considerations

When adding or modifying features:
- Preserve default `cd` behavior when no special features are invoked
- Use opt-in flags or environment variables for new behaviors
- Provide clear feedback for errors
- Consider performance impact on frequently-used command

## Dependencies

- Minimize external dependencies
- Document any required tools or utilities
- Provide fallback behavior when optional dependencies are missing
