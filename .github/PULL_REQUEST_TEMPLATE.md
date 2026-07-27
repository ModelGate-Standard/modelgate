**What this changes and why**

**Checklist**

- [ ] `python3 conformance/runner.py` passes (required if this touches `modelgate-core`)
- [ ] If this changes verdict/threshold behavior, `specs/mgs/MGS-1.0.md` §8 versioning implications are addressed (this is a spec change, not a patch, if so — see `CONTRIBUTING.md`)
- [ ] If this adds a Reader, checker logic still lives only in `modelgate-core` (see `CONTRIBUTING.md`)
- [ ] New/changed behavior has a conformance fixture, or an explanation of why one isn't needed

**Related issue(s)**
