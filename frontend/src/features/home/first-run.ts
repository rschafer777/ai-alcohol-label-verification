export const FIRST_RUN_KEY = "lv.firstRunDismissed";

export function readFirstRunDismissed(): boolean {
  try {
    return window.localStorage.getItem(FIRST_RUN_KEY) === "1";
  } catch {
    return false;
  }
}

export function writeFirstRunDismissed(): void {
  try {
    window.localStorage.setItem(FIRST_RUN_KEY, "1");
  } catch {
    /* storage unavailable: the tips simply show again next time */
  }
}
