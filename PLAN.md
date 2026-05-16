# AstroBob Testing & Enhancement Plan

## Issues Identified

### 1. **CRITICAL: Deprecated `datetime.utcnow()` Usage**
**Location:** [`src/astrobob/core/store.py`](src/astrobob/core/store.py:206)
- Lines 206, 250, 295
- **Issue:** `datetime.utcnow()` is deprecated in Python 3.12+
- **Impact:** Will cause deprecation warnings and potential future breakage
- **Fix:** Replace with `datetime.now(timezone.utc)`

### 2. **Missing CLI Command: `recall`**
**Location:** [`src/astrobob/cli/memory_cmd.py`](src/astrobob/cli/memory_cmd.py)
- **Issue:** No `recall` command in CLI, only available via MCP server
- **Impact:** Users cannot search memories from command line
- **Fix:** Add `recall` command to memory_cmd.py

### 3. **Duplicate Error Handling Code**
**Location:** [`src/astrobob/cli/memory_cmd.py`](src/astrobob/cli/memory_cmd.py:504-505)
- Lines 504-505 contain duplicate error handling
- **Impact:** Dead code, potential confusion
- **Fix:** Remove duplicate lines

## Enhancement Plan

### Phase 1: Fix Critical Issues
1. **Replace deprecated `datetime.utcnow()`**
   - Update all 3 occurrences in [`store.py`](src/astrobob/core/store.py)
   - Import `timezone` from datetime module
   - Change `datetime.utcnow()` → `datetime.now(timezone.utc)`

2. **Remove duplicate code**
   - Delete lines 504-505 in [`memory_cmd.py`](src/astrobob/cli/memory_cmd.py)

### Phase 2: Add CLI Recall Command
1. **Implement `recall` command in [`memory_cmd.py`](src/astrobob/cli/memory_cmd.py)**
   - Add new `@app.command()` function
   - Parameters:
     - `query` (required): Search query
     - `--project/-p`: Project filter
     - `--type/-t`: Memory type filter (multiple)
     - `--tag`: Tag filter (multiple)
     - `--limit/-l`: Result limit (default 10)
     - `--min-importance/-i`: Minimum importance
   - Use [`MemoryRetriever`](src/astrobob/core/retriever.py) for search
   - Display results in rich table format

2. **Update CLI imports**
   - Import `MemoryRetriever` in [`memory_cmd.py`](src/astrobob/cli/memory_cmd.py)

### Phase 3: Comprehensive Testing

#### Unit Tests
1. **Test `datetime` fixes**
   - Verify timezone-aware timestamps
   - Check ISO format output
   - Ensure backward compatibility

2. **Test recall command**
   - Query with various filters
   - Test memory type routing
   - Verify result formatting
   - Test error handling

#### Integration Tests
1. **End-to-end memory workflow**
   - `remember` → store memory
   - `recall` → retrieve memory
   - `reflect` → create procedural
   - `audit` → view provenance
   - `forget` → soft delete

2. **MCP server integration**
   - Test all 5 MCP tools
   - Verify recall works via MCP
   - Check memory persistence

#### Manual Testing Scenarios
1. **CLI recall command**
   ```bash
   # Basic search
   astrobob memory recall "how to add MCP tool" --project astrobob
   
   # Filtered search
   astrobob memory recall "API patterns" --type procedural --min-importance 4
   
   # Tagged search
   astrobob memory recall "authentication" --tag auth --tag security
   ```

2. **MCP server recall**
   - Test via MCP Inspector
   - Verify query intent routing
   - Check ranking algorithm

3. **Memory lifecycle**
   - Create semantic memory
   - Create episodic memory
   - Reflect to create procedural
   - Recall all types
   - Audit trail verification

### Phase 4: Validation & Documentation

1. **Run all tests**
   - Execute unit tests
   - Run integration tests
   - Perform manual testing

2. **Update documentation**
   - Add recall command to CLI reference
   - Document query intent routing
   - Add usage examples

3. **Verify fixes**
   - No deprecation warnings
   - All tests pass
   - CLI recall works correctly

## Test Execution Plan

### Step 1: Fix Issues
- [ ] Replace `datetime.utcnow()` in [`store.py`](src/astrobob/core/store.py)
- [ ] Remove duplicate code in [`memory_cmd.py`](src/astrobob/cli/memory_cmd.py)

### Step 2: Add Recall Command
- [ ] Implement `recall` function in [`memory_cmd.py`](src/astrobob/cli/memory_cmd.py)
- [ ] Add imports for `MemoryRetriever`
- [ ] Format output with rich tables

### Step 3: Test Fixes
- [ ] Run existing unit tests
- [ ] Test datetime changes
- [ ] Verify no deprecation warnings

### Step 4: Test Recall Command
- [ ] Test basic recall
- [ ] Test with filters
- [ ] Test query intent routing
- [ ] Test error cases

### Step 5: Integration Testing
- [ ] Test full memory workflow
- [ ] Test MCP server integration
- [ ] Verify memory persistence

### Step 6: Final Validation
- [ ] All tests pass
- [ ] No errors or warnings
- [ ] Documentation updated

## Success Criteria

✅ No deprecation warnings from datetime usage
✅ CLI recall command works correctly
✅ All existing tests pass
✅ New recall command tests pass
✅ Integration tests pass
✅ Manual testing scenarios complete
✅ Documentation updated

## Files to Modify

1. [`src/astrobob/core/store.py`](src/astrobob/core/store.py) - Fix datetime usage
2. [`src/astrobob/cli/memory_cmd.py`](src/astrobob/cli/memory_cmd.py) - Add recall command, remove duplicate code
3. Test files (if needed) - Add new tests

## Estimated Effort

- **Phase 1 (Fixes):** 15 minutes
- **Phase 2 (Recall Command):** 30 minutes
- **Phase 3 (Testing):** 45 minutes
- **Phase 4 (Validation):** 15 minutes
- **Total:** ~2 hours

## Risk Assessment

**Low Risk:**
- datetime fixes are straightforward replacements
- Recall command follows existing patterns
- No breaking changes to API

**Mitigation:**
- Thorough testing before deployment
- Backward compatibility maintained
- Clear documentation of changes