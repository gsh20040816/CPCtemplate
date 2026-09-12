#include <cassert>
#include <pthread.h>

#ifndef CPC_STACK_BYTES
#define CPC_STACK_BYTES (256ULL << 20)
#endif

int cpc_entry();

void *run_driver(void *)
{
    cpc_entry();
    return nullptr;
}

int main()
{
    pthread_attr_t attr;
    assert(pthread_attr_init(&attr) == 0);
    assert(pthread_attr_setstacksize(&attr, CPC_STACK_BYTES) == 0);
    pthread_t thread;
    assert(pthread_create(&thread, &attr, run_driver, nullptr) == 0);
    assert(pthread_attr_destroy(&attr) == 0);
    assert(pthread_join(thread, nullptr) == 0);
}
