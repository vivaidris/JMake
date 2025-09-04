# Auto-generated Makefile for JavaTest123
JAVAC=javac
JAVA=java
JFLAGS=

all: myapp

mylib: src/mylib/Lib.class

myapp: src/main/Main.class src/mylib/Lib.class

%.class: %.java
	$(JAVAC) -cp src $(JFLAGS) $<

clean:
	rm -f **/*.class *.class
