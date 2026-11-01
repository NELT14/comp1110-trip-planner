# HKU Lunch Planner

Live website: https://nelt14.github.io/comp1110-trip-planner/

The website runs entirely in the browser. It reads the two Excel files in Data using the bundled SheetJS 0.20.3 library (Apache 2.0; see vendor/LICENSE). GitHub Pages publishes main from the repository root. Commit and push updated Excel files to update the online data, then refresh the website after deployment. The website cannot see unsaved or local-only Excel changes.


Double-click **Start Lunch Planner.command** on this Mac. A Terminal window starts the app and your browser opens its interface. Keep Terminal open while using it; press Control+C there to stop. No packages or internet connection are needed. This uses the Python installation already available on this Mac.

Select the starting and next-class locations, check the departure time, and press **Compare restaurants**. Equal totals share a rank. The calculation is outbound walking + waiting until food arrives + onward walking. Eating is excluded. Departure defaults to the computer's current local time and can be changed for scenarios.

The app reads the two Excel files from `../Data/`. Save Excel edits and refresh the page to reload them in local mode. Timings are synthetic minutes, not distances or live predictions. Each travel pair works in either direction. Restaurant names must match across both files. Missing timings are unavailable, never zero. At a time-band boundary the next band applies; arrivals at 19:00 or later have no estimate.

To load newly added campus locations into the dropdowns, refresh the page. Keep the first data worksheet and its header layout in each workbook. No Excel application needs to be running.

Run the calculation tests with `python3 -m unittest test_app.py` from this folder.
