# Spec Builder Tips

## If It Gets Stuck

1. **Type 'skip'** - Immediately generate spec with current info
2. **Type 'done'** - Same as skip
3. **Press Ctrl+C** - Cancel and try again with simpler description
4. **Max 6 turns** - Auto-generates after 6 conversation turns
5. **Auto-timeout** - 120 seconds per response, 3 minutes for spec generation

## Best Practices

**Quick Mode** (1-2 minutes):
```bash
python spec_builder.py
# Your idea: A todo app
# [Answer 1-2 questions]
# Type: skip
```

**Detailed Mode** (3-5 minutes):
```bash
python spec_builder.py  
# Your idea: A comprehensive habit tracker with analytics...
# [Answer all questions thoughtfully]
# Type: done
```

## Spec Format

The generated spec will be in **XML format** with:
- `<project_specification>` root
- `<technology_stack>` - Exact versions
- `<core_features>` - 5-10 detailed categories
- `<design_system>` - Colors (hex), typography
- `<implementation_steps>` - 8-12 numbered phases
- `<success_criteria>` - Measurable outcomes

## Common Issues

**Empty Response**: Auto-detected and handled
**Network Timeout**: Auto-timeout after 120 seconds, retries or uses partial spec
**Conversation Loop**: Max 6 turns prevents infinite loops
**Stuck on Input**: Type 'skip' to fast-forward
**Hung Response**: Automatic timeout triggers spec generation after 2-3 minutes
