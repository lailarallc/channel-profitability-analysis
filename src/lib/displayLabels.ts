// Public display labels for trade partners (rule decided 2026-11-05): a
// Cinderhaven dollar figure never sits beside a real retailer or distributor
// name. Data keeps real names (channel_name); only rendered text goes through
// here. The map is vendored from cinderhaven-data-platform by
// scripts/refresh_canonical.py; scripts/check_retailer_labels.py enforces it.
import labels from '../../reference/retailer_display_labels.json';

const LABELS = new Map<string, string>(
  [...Object.values(labels.retailers), ...Object.values(labels.distributors)]
    .map(p => [p.name, p.label]),
);

/** Display label for a channel name. Capitalized by default (table, legend,
 *  chart label, sentence start); pass false for mid-sentence use. Names not in
 *  the map (DTC) pass through unchanged. */
export function channelLabel(name: string, capitalize = true): string {
  const label = LABELS.get(name) ?? name;
  return capitalize ? label.charAt(0).toUpperCase() + label.slice(1) : label;
}
