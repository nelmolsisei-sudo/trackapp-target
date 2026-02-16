# trackapp-target

**A multi-domain target codebase for RL evaluation -- Django web application + Solidity smart contracts -- purpose-built to test autonomous coding agents across the full stack.**

Paired with [trackapp-rl-env](https://github.com/nelmolsisei-sudo/trackapp-rl-env).

---

## The Role of Target Codebases in RL

Reinforcement learning for code agents requires two things: environments that present tasks, and codebases that *are* the tasks. The environment handles orchestration, tooling, and grading. The target codebase provides the substrate -- the actual software an agent must understand, navigate, and modify.

The quality of the target codebase is the single most important variable in determining whether an RL environment produces useful training signal or noise. Synthetic codebases -- generated to have exactly one bug in exactly one function with exactly one fix -- teach agents to pattern-match against artificial structure. Real codebases teach agents to reason under the conditions that actually matter: ambiguous variable names, implicit conventions, business logic distributed across files, and the accumulated decisions of real development.

This repository is a real application. It was built to manage human athletic performance data -- competition results, personal records, milestone tracking, qualifying standards, team rosters, and seasonal statistics. It has real Django models with foreign key chains, real views with authentication logic, real forms with validation, real templates with conditional rendering, and real bugs that emerged from real development.

It is precisely the kind of codebase that separates agents that can complete benchmarks from agents that can do work.

## What the Application Does

`trackapp-target` is a Django 3.2 web application for managing track and field athletics programs. It supports:

- **Athlete management**: user registration, profile pages, team membership, gender-based filtering
- **Competition tracking**: meets (competitions) with dates, descriptions, teams, and seasons
- **Result recording**: individual performance results linked to athletes, events, and meets
- **Statistical computation**: automatic calculation of personal records, rankings, milestone detection (e.g., "Broke 5:00 in the mile"), and qualifying standard matching
- **Team administration**: team creation, coach/athlete roster management
- **Data import**: spreadsheet-based bulk import of results and qualifying standards
- **Qualifying standards**: configurable qualification levels by event, season, and gender

### Technical Stack

- **Django 3.2.5** with SQLite
- **django-crispy-forms** for form rendering
- **openpyxl** for spreadsheet import
- Custom `calculate_result_stats()` function that computes personal bests, milestones, and qualification matches across an athlete's full result history

## Branch Structure

This repository uses a **3-branch pattern** for each RL task. For every task defined in `trackapp-rl-env`, three branches exist here:

| Branch | Purpose |
|--------|---------|
| `{task}_baseline` | Contains the bug. This is what the agent sees. |
| `{task}_golden` | Contains the reference fix. Used for validation. |
| `{task}_test` | Contains the hidden test suite. Never visible to the agent. |

### Current Task Branches

**Django branches** (share history with `main`):

```
main                              # Base application with infrastructure fixes

fix_result_crud_baseline          # Missing calculate_result_stats calls, incorrect context vars
fix_result_crud_golden            # Correct stat recalculation and template context
fix_result_crud_test              # 11 tests across add/edit/delete result views

fix_profile_404_baseline          # User.objects.get() crashes on missing users
fix_profile_404_golden            # get_object_or_404() for proper 404 handling
fix_profile_404_test              # 2 tests for 404/200 behavior

fix_merge_meet_auth_baseline      # merge_meet view missing @login_required
fix_merge_meet_auth_golden        # @login_required decorator added
fix_merge_meet_auth_test          # 2 tests for auth redirect behavior

fix_register_validation_baseline  # No password length validation
fix_register_validation_golden    # len(password) < 8 check added
fix_register_validation_test      # 4 tests for empty/short/valid/mismatch passwords

fix_remove_safety_baseline        # remove_coach/athlete processes on GET
fix_remove_safety_golden          # POST-only enforcement on both views
fix_remove_safety_test            # 4 tests for GET-safe/POST-active behavior
```

**Solidity branches** (orphan -- completely separate file tree, no Django code):

```
smart_contract_erc20_baseline     # ERC-20 token with missing access control, validation gaps
smart_contract_erc20_golden       # Secure implementation with require() guards
smart_contract_erc20_test         # 11 Forge tests covering mint, transfer, transferFrom security
```

The Solidity branches use **orphan branches** -- they share no commit history with the Django branches and contain a pure Foundry project structure (`foundry.toml`, `src/`, `test/`). This keeps the file trees completely separate: when an agent checks out a smart contract baseline, it sees only the Solidity project, not the Django application.

At build time, the RL environment clones this repository, generates diff patches between branches, and uses them for scenario setup and grading. The agent never sees the golden or test branches -- it works only with the baseline code and a natural language description of the problem.

## Why This Matters Beyond Track and Field

The athletic performance domain is a microcosm of the broader category of problems that remain stubbornly resistant to automation: **coordination-heavy record-keeping where domain expertise is embedded in business logic rather than documented in specifications.**

Every organization that manages human performance data -- whether that's athletic results, student assessments, clinical outcomes, or financial portfolios -- shares the same structural characteristics: hierarchical entity relationships, temporal ordering that affects computation, qualification thresholds that depend on context, and statistical aggregation that must remain consistent through CRUD operations.

The bugs in this codebase are not academic. Missing stat recalculation after a record is added. Destructive operations accessible without authentication. State mutations triggered by safe HTTP methods. These are the same categories of bugs that exist in every production Django application, every Rails application, every real-world web system built under time pressure by real engineers.

Training agents to fix these bugs -- autonomously, reliably, verifiably -- is a necessary step toward building AI systems that can be trusted with real software maintenance at scale.

## Why Smart Contracts Belong in the Same Target Repo

The addition of Solidity smart contract branches to this repository is deliberate. A single target repo that hosts both web2 (Django) and web3 (Solidity/EVM) tasks forces the RL evaluation framework to be genuinely framework-agnostic -- the same environment, the same grading infrastructure, the same 3-branch pattern must work across fundamentally different languages, runtimes, and testing frameworks.

Smart contract security is arguably the highest-stakes application of autonomous coding. Contracts deployed to EVM-compatible chains like Ethereum and Monad are **immutable** -- there is no post-deployment hotfix. A missing `require` statement in an ERC-20 token can be exploited within seconds of deployment, and the funds are gone. The total value lost to smart contract vulnerabilities exceeds $5 billion. Every major exploit -- from the DAO hack to Wormhole to Ronin Bridge -- was caused by a vulnerability that a careful auditor would have caught, but that was missed under the time pressure and complexity of real development.

Building agents that can reliably audit and fix these vulnerabilities requires RL environments that test against realistic contract implementations, not synthetic puzzles. The ERC-20 task in this repository presents the same categories of bugs that appear in production DeFi protocols: missing access control, insufficient balance validation, and absent zero-address guards. These are the foundational patterns that, when missed, have historically cost hundreds of millions of dollars.

## Roadmap

The current task inventory spans Django view-level bugs and ERC-20 smart contract vulnerabilities. The planned expansion includes:

- **Smart contract expansion**: ERC-721 (NFT) implementations, DeFi protocol interactions (lending pools, AMMs), multi-contract upgrade patterns, gas optimization targeting Monad and other high-performance EVM chains
- **Multi-file Django tasks**: bugs that span models, views, forms, and templates
- **Logic tasks**: errors in `calculate_result_stats` and milestone computation that require understanding domain-specific math
- **Architecture tasks**: URL routing issues, migration problems, settings misconfiguration
- **Web2/Web3 bridge tasks**: fixing backend services that interact with on-chain state (oracles, indexers, transaction relayers)

The depth and breadth of this target codebase will grow in proportion to the complexity of the tasks it supports, across both traditional web applications and on-chain protocols.

## License

MIT
