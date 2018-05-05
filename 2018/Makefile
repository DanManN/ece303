INPUT:= input
OUTPUT:= output
test:
	time python2 receiver.py > $(OUTPUT) & python2 sender.py < $(INPUT) &
cat:
	cat Sup*.log
diff:
	diff $(INPUT) $(OUTPUT)
kill:
	pkill python2
clean:
	rm *.log output *.pyc
