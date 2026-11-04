# HKU Lunch Planner

Live website: https://nelt14.github.io/comp1110-trip-planner/

The website runs entirely in the browser. It reads the Classrooms and Restaurants sheets in `Data/Eateries and Uni locations.xlsx` using bundled SheetJS 0.20.3 (Apache 2.0; see vendor/LICENSE). GitHub Pages publishes main from the repository root. Commit and push workbook changes to update the online list, then refresh after deployment. Local-only or unsaved changes are not visible online.

`estimates.js` assigns synthetic walking and waiting estimates to every classroom/eatery pair. Walking assumes 2 minutes within a building, 6 within an area, or 12 between areas, plus a rounded-up half-minute per floor difference. Multi-floor locations use ground level. These are scenario assumptions, not measured routes. The workbook's area labels are used as supplied. Restaurant-specific waiting assumptions use four periods, with zero wait for vending machines. Edit the waiting map to refine those assumptions.

The survey asks for start, restaurant, destination, visit date, arrival time, waiting time and both walking legs. It downloads one CSV response locally. It does not transmit answers, store them in a database, or alter the estimates. Users must share that file with the team separately. Animations respect the device's reduced-motion setting.


Double-click **Start Lunch Planner.command** on this Mac. A Terminal window starts the app and your browser opens its interface. Keep Terminal open while using it; press Control+C there to stop. No packages or internet connection are needed. This uses the Python installation already available on this Mac.

Select the starting and next-class locations, check the departure time, and press **Compare restaurants**. Equal totals share a rank. The calculation is outbound walking + waiting until food arrives + onward walking. Eating is excluded. Departure defaults to the computer's current local time and can be changed for scenarios.

Save workbook edits and refresh the page to reload them in local mode. Timings are synthetic minutes, not distances or live predictions. Each travel pair works in either direction. Missing timings are unavailable, never zero. At a time-band boundary the next band applies; arrivals at 19:00 or later have no estimate. The original sample Excel files remain available as earlier examples.

To load newly added campus locations into the dropdowns, refresh the page. Keep the named Classrooms and Restaurants sheets and their header layouts in the workbook. No Excel application needs to be running.

Run full-list browser-calculation tests with `node test_estimates.js` from this folder. Legacy Python sample tests remain available through `python3 -m unittest test_app.py`.
