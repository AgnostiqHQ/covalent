all:
	gcc -shared -fPIC -o libtest.so test.c

clean:
	rm -f test.so
