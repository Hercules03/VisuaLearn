#!/bin/bash
# Quick response inspection script for debugging orchestrator output

RESPONSES_DIR="app/responses"

if [ ! -d "$RESPONSES_DIR" ]; then
    echo "❌ Responses directory not found: $RESPONSES_DIR"
    exit 1
fi

show_help() {
    echo "Usage: ./inspect_responses.sh [command] [args]"
    echo ""
    echo "Commands:"
    echo "  list              Show all stored requests"
    echo "  latest            Show latest 5 responses"
    echo "  request <id>      Show all responses for a request ID"
    echo "  scores <id>       Show review scores for a request"
    echo "  xml <id>          Extract XML files for a request"
    echo "  compare <id>      Compare XML before/after refinements"
    echo "  plan <id>         Show planning output for a request"
    echo "  clean             Remove all stored responses"
    echo ""
    echo "Examples:"
    echo "  ./inspect_responses.sh list"
    echo "  ./inspect_responses.sh latest"
    echo "  ./inspect_responses.sh request abc12345"
    echo "  ./inspect_responses.sh scores abc12345"
    echo "  ./inspect_responses.sh xml abc12345"
}

list_requests() {
    echo ""
    echo "📊 Stored Requests"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    jq -s 'group_by(.request_id) | map({
        request_id: .[0].request_id,
        timestamp: .[0].timestamp,
        steps: [.[].step] | unique | join(", ")
    }) | sort_by(.timestamp) | reverse | .[]' \
    "$RESPONSES_DIR"/*.json 2>/dev/null | \
    jq -r '"  \(.request_id | .[0:8])  \(.timestamp[0:19])  \(.steps)"' || \
    echo "  No responses found"

    echo ""
}

show_latest() {
    echo ""
    echo "⏰ Latest 5 Responses"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    ls -t "$RESPONSES_DIR"/*.json 2>/dev/null | head -5 | while read file; do
        basename="$(basename "$file")"
        timestamp=$(jq -r '.timestamp[11:19]' "$file" 2>/dev/null)
        step=$(jq -r '.step' "$file" 2>/dev/null)
        request_id=$(jq -r '.request_id' "$file" 2>/dev/null)

        printf "  %s  %-30s [%s] %s\n" "$timestamp" "$step" "$request_id" "$basename"
    done

    echo ""
}

show_request() {
    local request_id="$1"

    if [ -z "$request_id" ]; then
        echo "❌ Request ID required"
        exit 1
    fi

    echo ""
    echo "📋 Request: $request_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for file in "$RESPONSES_DIR"/*.json; do
        grep -q "\"request_id\": \"$request_id\"" "$file" 2>/dev/null || continue

        basename="$(basename "$file")"
        step=$(jq -r '.step' "$file")
        timestamp=$(jq -r '.timestamp' "$file")

        echo ""
        echo "📄 $basename"
        echo "   Step: $step"
        echo "   Time: $timestamp"

        case "$step" in
            "planning_agent")
                jq '.data | {concept, diagram_type, components: (.components | length), relationships: (.relationships | length)}' "$file"
                ;;
            "diagram_generation")
                echo "   XML Size: $(jq -r '.xml_length' "$file") bytes"
                ;;
            "review_agent")
                jq '.data | {score, approved, iteration}' "$file"
                ;;
            "mcp_refinement")
                before=$(jq -r '.xml_before_length' "$file")
                after=$(jq -r '.xml_after_length' "$file")
                echo "   XML Before: $before bytes"
                echo "   XML After:  $after bytes"
                echo "   Change: $((after - before)) bytes"
                ;;
            "svg_conversion")
                echo "   SVG Size: $(jq -r '.svg_length' "$file") bytes"
                ;;
        esac
    done

    echo ""
}

show_scores() {
    local request_id="$1"

    if [ -z "$request_id" ]; then
        echo "❌ Request ID required"
        exit 1
    fi

    echo ""
    echo "📈 Review Scores: $request_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    printf "  Iter  Score  Approved  Feedback\n"
    printf "  ────  ─────  ────────  ────────────────────────────────────\n"

    for file in "$RESPONSES_DIR"/03_review_*.json; do
        grep -q "\"request_id\": \"$request_id\"" "$file" 2>/dev/null || continue

        iteration=$(jq -r '.iteration' "$file")
        score=$(jq -r '.data.score' "$file")
        approved=$(jq -r '.data.approved' "$file")
        feedback=$(jq -r '.data.feedback' "$file" | cut -c1-40)

        printf "  %d     %3d    %-8s  %s\n" "$iteration" "$score" "$approved" "$feedback"
    done

    echo ""
}

extract_xml() {
    local request_id="$1"

    if [ -z "$request_id" ]; then
        echo "❌ Request ID required"
        exit 1
    fi

    echo ""
    echo "💾 Extracting XML files for: $request_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    count=0
    for file in "$RESPONSES_DIR"/*.json; do
        grep -q "\"request_id\": \"$request_id\"" "$file" 2>/dev/null || continue

        step=$(jq -r '.step' "$file")

        if [ "$step" = "diagram_generation" ]; then
            outfile="extracted_generation_${request_id}.xml"
            jq -r '.xml_full' "$file" > "$outfile"
            echo "✅ $outfile ($(jq -r '.xml_length' "$file") bytes)"
            count=$((count + 1))
        fi

        if [ "$step" = "svg_conversion" ]; then
            outfile="extracted_svg_${request_id}.svg"
            jq -r '.svg_full' "$file" > "$outfile"
            echo "✅ $outfile ($(jq -r '.svg_length' "$file") bytes)"
            count=$((count + 1))
        fi

        if [[ "$step" =~ "refinement" ]]; then
            iteration=$(jq -r '.iteration' "$file")
            outfile_before="extracted_refinement_iter${iteration}_before_${request_id}.xml"
            outfile_after="extracted_refinement_iter${iteration}_after_${request_id}.xml"
            jq -r '.xml_before_full' "$file" > "$outfile_before"
            jq -r '.xml_after_full' "$file" > "$outfile_after"
            echo "✅ $outfile_before"
            echo "✅ $outfile_after"
            count=$((count + 2))
        fi
    done

    if [ $count -eq 0 ]; then
        echo "❌ No XML files found for request: $request_id"
    else
        echo ""
        echo "📁 Extracted $count files"
    fi
    echo ""
}

compare_xml() {
    local request_id="$1"

    if [ -z "$request_id" ]; then
        echo "❌ Request ID required"
        exit 1
    fi

    echo ""
    echo "🔄 XML Refinement Changes: $request_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    printf "  Iter  Before  After  Change  Feedback\n"
    printf "  ────  ──────  ─────  ──────  ────────────────────────────────\n"

    for file in "$RESPONSES_DIR"/03b_refinement_*.json; do
        grep -q "\"request_id\": \"$request_id\"" "$file" 2>/dev/null || continue

        iteration=$(jq -r '.iteration' "$file")
        before=$(jq -r '.xml_before_length' "$file")
        after=$(jq -r '.xml_after_length' "$file")
        change=$((after - before))
        feedback=$(jq -r '.feedback' "$file" | cut -c1-30)

        printf "  %d     %6d  %5d  %+6d  %s\n" "$iteration" "$before" "$after" "$change" "$feedback"
    done

    echo ""
}

show_plan() {
    local request_id="$1"

    if [ -z "$request_id" ]; then
        echo "❌ Request ID required"
        exit 1
    fi

    echo ""
    echo "🎯 Planning Output: $request_id"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for file in "$RESPONSES_DIR"/01_planning_*.json; do
        grep -q "\"request_id\": \"$request_id\"" "$file" 2>/dev/null || continue

        echo ""
        jq '.data' "$file"
    done

    echo ""
}

cleanup() {
    count=$(find "$RESPONSES_DIR" -name "*.json" | wc -l)

    if [ $count -eq 0 ]; then
        echo "✅ No responses to clean up"
        return
    fi

    echo ""
    echo "🗑️  Found $count response files"
    read -p "Delete all? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$RESPONSES_DIR"/*.json
        echo "✅ Cleaned up all responses"
    else
        echo "❌ Cancelled"
    fi

    echo ""
}

# Main
case "${1:-list}" in
    help|-h|--help)
        show_help
        ;;
    list)
        list_requests
        ;;
    latest)
        show_latest
        ;;
    request)
        show_request "$2"
        ;;
    scores)
        show_scores "$2"
        ;;
    xml)
        extract_xml "$2"
        ;;
    compare)
        compare_xml "$2"
        ;;
    plan)
        show_plan "$2"
        ;;
    clean)
        cleanup
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
