"""Auto-routing: decides between direct output and map mode."""

from pathlib import Path
from .models import Result


DEFAULT_THRESHOLD = 4000


def route(filepath: Path, args) -> Result:
    """Route a file to the appropriate conversion mode."""
    from ..extractors import get_extractor

    extractor = get_extractor(filepath)
    ext = filepath.suffix.lower()

    # --grep mode
    if args.grep:
        from .grep import grep_document
        return grep_document(filepath, extractor, args.grep)

    # --schema-only (xlsx/csv)
    if getattr(args, "schema_only", False):
        content = extractor.extract_schema(filepath)
        if not content:
            content = extractor.extract(filepath)
        return Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="direct",
            content=content,
            total_tokens=len(content) // 4,
        )

    # --sample N (xlsx/csv)
    if getattr(args, "sample", None) is not None:
        content = extractor.extract_sample(filepath, args.sample)
        if not content:
            content = extractor.extract(filepath)
        return Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="direct",
            content=content,
            total_tokens=len(content) // 4,
        )

    # --tables-only
    if getattr(args, "tables_only", False):
        content = extractor.extract_tables(filepath)
        if not content:
            content = "*No tables found in document.*\n"
        return Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="direct",
            content=content,
            total_tokens=len(content) // 4,
        )

    # --sections (requires segmentation)
    if getattr(args, "sections", None):
        from .segmenter import segment_document
        sections = segment_document(filepath, extractor)
        requested = set(s.strip() for s in args.sections.split(","))
        matched = [s for s in sections if s.id in requested]
        if not matched:
            content = f"*No sections matching {args.sections} found.*\n"
        else:
            content = "\n\n".join(s.content for s in matched).strip() + "\n"
        total = sum(s.tokens for s in matched)
        result = Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="sections",
            content=content,
            sections=matched,
            total_tokens=total,
        )
        # Apply budget if also specified
        if getattr(args, "budget", None) and total > args.budget:
            from .budget import compress
            result = compress(result, args.budget)
        return result

    # Force full extraction (--all or pull subcommand)
    force_full = getattr(args, "all", False) or getattr(args, "command", None) == "pull"

    # Force map mode (probe subcommand)
    force_map = getattr(args, "command", None) == "probe"

    if force_full and not force_map:
        content = extractor.extract(filepath)
        result = Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="direct",
            content=content,
            total_tokens=len(content) // 4,
        )
        if getattr(args, "budget", None) and result.total_tokens > args.budget:
            from .budget import compress
            from .segmenter import segment_document
            sections = segment_document(filepath, extractor)
            result.sections = sections
            result = compress(result, args.budget)
        return result

    # Auto-routing: estimate tokens, decide mode
    estimated = extractor.estimate_tokens(filepath)
    threshold = getattr(args, "budget", None) or DEFAULT_THRESHOLD

    if not force_map and estimated <= threshold:
        # Small file: direct output (v1 behavior)
        content = extractor.extract(filepath)
        return Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="direct",
            content=content,
            total_tokens=len(content) // 4,
        )
    else:
        # Large file or forced probe: map mode
        from .segmenter import segment_document
        from .mapper import render_map

        sections = segment_document(filepath, extractor)
        total_tokens = sum(s.tokens for s in sections)

        # Detect quality issues
        quality = "complete"
        quality_note = None
        warnings = []
        for s in sections:
            warnings.extend(s.warnings)
        if warnings:
            quality = "partial"
            quality_note = "; ".join(set(warnings))

        result = Result(
            source=filepath.name,
            format=ext.lstrip("."),
            mode="map",
            quality=quality,
            quality_note=quality_note,
            sections=sections,
            total_tokens=total_tokens,
            warnings=warnings,
        )
        result.content = render_map(filepath, result)
        return result
