"""CLI entry point for playbook_validator.

Usage:
    python -m playbook_validator validate-docs [--root PATH]
    python -m playbook_validator validate-skills [--root PATH]
    python -m playbook_validator validate-landscape [--path PATH]
    python -m playbook_validator validate-adrs [--dir PATH]
    python -m playbook_validator validate-risk-assessment [--path PATH]
    python -m playbook_validator doctor [--json] [--plan PATH] [--root PATH]
    python -m playbook_validator audit-repo [--path PATH]
    python -m playbook_validator generate-index [--check] [--root PATH]
    python -m playbook_validator pre-deploy [--path PATH]
    python -m playbook_validator ensure-contract [--root PATH] [--no-fetch]
"""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger("playbook_validator")


def cmd_validate_docs(args: argparse.Namespace) -> int:
    from playbook_validator.validate_docs import find_content_files, validate_doc_frontmatter

    root = Path(args.root)
    files = find_content_files(root)
    total_errors = 0

    print("=== Frontmatter Validation ===")
    for f in files:
        errors, warnings = validate_doc_frontmatter(f)
        for e in errors:
            print(f"ERROR: {e}")
            total_errors += 1
        for w in warnings:
            print(f"WARNING: {w}")
        if not errors:
            print(f"  OK: {f.relative_to(root)}")

    print(f"\n=== Summary ===\nErrors: {total_errors}")
    if total_errors > 0:
        print(f"FAILED — {total_errors} error(s) found")
        return 1
    print("All validations passed.")
    return 0


def cmd_validate_skills(args: argparse.Namespace) -> int:
    from playbook_validator.validate_skills import find_skill_dirs, validate_skill

    root = Path(args.root)
    skill_dirs = find_skill_dirs(root)
    total_errors = 0

    print("=== Skills Validation ===")
    for sd in skill_dirs:
        errors, warnings = validate_skill(sd)
        for e in errors:
            print(f"ERROR: {e}")
            total_errors += 1
        for w in warnings:
            print(f"WARNING: {w}")
        if not errors:
            print(f"  OK: {sd.name}")

    print(f"\n=== Summary ===\nSkills found: {len(skill_dirs)}\nErrors: {total_errors}")
    if total_errors > 0:
        print(f"FAILED — {total_errors} error(s) found")
        return 1
    print("All skills validations passed.")
    return 0


def cmd_validate_landscape(args: argparse.Namespace) -> int:
    from playbook_validator.validate_landscape import validate_landscape

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 2

    errors, warnings, count = validate_landscape(path)
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if errors:
        print(f"FAILED: {len(errors)} error(s) found in {count} entries", file=sys.stderr)
        return 1
    print(f"OK: {count} entries validated, all checks passed")
    return 0


def cmd_validate_adrs(args: argparse.Namespace) -> int:
    from playbook_validator.validate_adrs import validate_adr_directory

    adr_dir = Path(args.dir)
    if not adr_dir.is_dir():
        print(f"ERROR: Directory not found: {adr_dir}", file=sys.stderr)
        return 2

    errors, warnings = validate_adr_directory(adr_dir)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"FAILED — {len(errors)} error(s) found")
        return 1
    print("All ADR validations passed.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    from playbook_validator.doctor import run_doctor

    root = Path(args.root)
    plan = args.plan if args.plan else None
    rc = run_doctor(root, plan_path=plan)

    if args.json:
        print(rc.to_json())
    else:
        print("\n═══ Agent Environment Doctor ═══\n")
        print(rc.format_text())
        if rc.exit_code == 0:
            print("\n  ✓ Environment is ready.")
        else:
            print(f"\n  ✗ {rc.checks_failed} item(s) need attention.")
            print("  Tip: After fixing, re-run the doctor.")
    return rc.exit_code


def cmd_audit_repo(args: argparse.Namespace) -> int:
    from playbook_validator.audit_repo import audit_repo

    repo = Path(args.path)
    rc = audit_repo(repo)
    print(rc.to_json())
    return rc.exit_code


def cmd_validate_plan(args: argparse.Namespace) -> int:
    from playbook_validator.validate_project_plan import validate_project_plan

    path = Path(args.path)
    errors, warnings = validate_project_plan(path)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s). Fix these before bootstrap.")
        return 1
    if warnings:
        print(f"\nPASSED with {len(warnings)} warning(s).")
    else:
        print("\nAll checks passed. Ready for bootstrap.")
    return 0


def cmd_validate_risk_assessment(args: argparse.Namespace) -> int:
    from playbook_validator.validate_risk_assessment import validate_risk_assessment

    path = Path(args.path)
    errors, warnings = validate_risk_assessment(path)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s) found")
        return 1
    if warnings:
        print(f"\nPASSED with {len(warnings)} warning(s)")
    else:
        print("\nAll risk assessment checks passed.")
    return 0


def cmd_new_project(args: argparse.Namespace) -> int:
    from playbook_validator.new_project import new_project

    target = Path(args.dir).resolve()
    playbook_root = Path(args.playbook_root).resolve()

    if not playbook_root.exists():
        print(f"ERROR: Playbook root not found: {playbook_root}", file=sys.stderr)
        return 2

    print(f"Bootstrapping new project at: {target}")
    print(f"Using playbook at: {playbook_root}")
    print()

    copied, skipped = new_project(target, playbook_root)

    for f in copied:
        print(f"  [COPIED] {f}")
    for f in skipped:
        print(f"  [SKIP]   {f}")

    print(f"\n  Copied: {len(copied)}  |  Skipped: {len(skipped)}")
    print()
    print("Next steps:")
    print(f"  1. cd {target}")
    print("  2. Edit PROJECT_PLAN.md — fill in project name, tech stack, compliance level")
    print("  3. Tell your AI agent: 'Bootstrap this project from PROJECT_PLAN.md'")
    return 0


def cmd_pre_deploy(args: argparse.Namespace) -> int:
    from playbook_validator.pre_deploy_checks import run_pre_deploy_checks

    repo = Path(args.path)
    rc = run_pre_deploy_checks(repo)
    print(rc.to_json())
    return rc.exit_code


def cmd_ensure_contract(args: argparse.Namespace) -> int:
    from playbook_validator.ensure_contract import ensure_contract

    result = ensure_contract(Path(args.root), allow_fetch=not args.no_fetch)
    if result.warning:
        print(f"WARNING: {result.warning}", file=sys.stderr)
    stream = sys.stdout if result.ok else sys.stderr
    print(f"{result.status.value}: {result.message}", file=stream)
    return result.exit_code


def cmd_landscape_check(args: argparse.Namespace) -> int:
    """Run the landscape monitor to check for federal AI guidance updates."""
    import landscape_monitor

    argv = ["--registry", args.registry]
    if args.output:
        argv.extend(["--output", args.output])
    if args.dry_run:
        argv.append("--dry-run")

    return landscape_monitor.main(argv)


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="playbook_validator", description="Playbook validation tools")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose/debug output")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("validate-docs", help="Validate document frontmatter")
    p.add_argument("--root", default=".", help="Repository root")

    p = sub.add_parser("validate-skills", help="Validate skill directories")
    p.add_argument("--root", default=".", help="Repository root")

    p = sub.add_parser("validate-landscape", help="Validate AI landscape registry")
    p.add_argument("--path", default="data/federal-ai-landscape.yaml")

    p = sub.add_parser("validate-adrs", help="Validate ADR files")
    p.add_argument("--dir", default="docs/adr", help="ADR directory")

    p = sub.add_parser("doctor", help="Check environment readiness")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--plan", help="Path to PROJECT_PLAN.md")
    p.add_argument("--root", default=".", help="Repository root")

    p = sub.add_parser("audit-repo", help="Audit repo compliance baseline")
    p.add_argument("--path", default=".", help="Repository path")

    p = sub.add_parser("generate-index", help="Generate INDEX.yaml")
    p.add_argument("--check", action="store_true", help="Check mode (exit 1 if stale)")
    p.add_argument("--root", default=".", help="Repository root")

    p = sub.add_parser("pre-deploy", help="Run pre-deployment security checks")
    p.add_argument("--path", default=".", help="Repository path")

    p = sub.add_parser(
        "ensure-contract",
        help="Deterministically ensure the universal behavioral contract is available (fail-closed)",
    )
    p.add_argument("--root", default=".", help="Working project root (where the cache lives)")
    p.add_argument("--no-fetch", action="store_true", help="Do not fetch; use only home path or existing cache")

    p = sub.add_parser("landscape-check", help="Check for federal AI guidance updates via RSS")
    p.add_argument("--registry", default="data/federal-ai-landscape.yaml", help="Path to landscape registry")
    p.add_argument("--output", help="Output path for diff report (default: stdout)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be checked")

    p = sub.add_parser("validate-plan", help="Validate PROJECT_PLAN.md")
    p.add_argument("--path", default="PROJECT_PLAN.md", help="Path to PROJECT_PLAN.md")

    p = sub.add_parser("validate-risk-assessment", help="Validate risk assessment worksheet")
    p.add_argument("--path", default="templates/risk-assessment.md", help="Path to risk assessment file")

    p = sub.add_parser("new-project", help="Bootstrap a new project from playbook templates")
    p.add_argument("--dir", required=True, help="Target directory for the new project")
    p.add_argument("--playbook-root", default=".", help="Path to the playbook repo root")

    return parser


# Command dispatch table
_COMMANDS = {
    "validate-docs": cmd_validate_docs,
    "validate-skills": cmd_validate_skills,
    "validate-landscape": cmd_validate_landscape,
    "validate-adrs": cmd_validate_adrs,
    "doctor": cmd_doctor,
    "audit-repo": cmd_audit_repo,
    "pre-deploy": cmd_pre_deploy,
    "ensure-contract": cmd_ensure_contract,
    "landscape-check": cmd_landscape_check,
    "validate-plan": cmd_validate_plan,
    "validate-risk-assessment": cmd_validate_risk_assessment,
    "new-project": cmd_new_project,
}


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(name)s: %(message)s",
    )

    if not args.command:
        parser.print_help()
        return 2

    try:
        if args.command == "generate-index":
            from playbook_validator.generate_index import main as gen_main

            return gen_main(["--root", args.root] + (["--check"] if args.check else []))

        return _COMMANDS[args.command](args)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        logger.debug("Full traceback:", exc_info=True)
        print(f"ERROR: Unexpected failure: {e}", file=sys.stderr)
        print("  Re-run with -v for debug output.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
