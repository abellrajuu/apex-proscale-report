### [SOLVED] Admin Portal Table Design Rules
**Page**: `/admin/portal`
**Design Rules established**:
1. Tables should use a 1-based sequential index (1, 2, 3...) for rows instead of displaying raw database IDs.
2. Use "Customer Name" as the column header (do not include "Plant" or "Conveyor No" columns to keep tables clean).
3. Timestamps should be labeled as "Completing Time" rather than "Exact Saved Timestamp".
4. Do not show "Storage Status" or "Server Synced" badges in this table.
5. Action column should be titled "Report" and the button text should be "VIEW REPORT" (all caps).
