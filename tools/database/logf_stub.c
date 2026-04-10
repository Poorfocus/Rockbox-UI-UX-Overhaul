/* Minimal stubs for database tool PCTOOL build on Win32 */
#include <time.h>
void logf_panic_dump(int *y) { (void)y; }
/* localtime_r is POSIX; Win32 uses localtime_s with reversed args */
struct tm *localtime_r(const time_t *timep, struct tm *result) {
    return localtime_s(result, timep) == 0 ? result : NULL;
}
