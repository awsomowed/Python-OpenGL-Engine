import traceback as tb
import time as t

def print_tb(trb):
	print(trb.tb_frame.stack[0])
	if trb.tb_next:
		print_tb(trb.tb_next)

def print_stack(trb):
	frame = trb.tb_frame
	print(trb)
	print(frame)
	fi = frame.__internals__
	stack = fi['f_back'].stack
	for i in range(len(stack)):
		print(stack[i])
	print_tb(trb)

def print_error(error,*args):
	tb.print_exception(type(error),error,error.__traceback__)

def print_error_c(error, *args):
	print('------------------------------')
	print(type(error).__name__)
	print(error)
	print_stack(error.__traceback__)
	print('------------------------------')

def print_error_tb(error, *args):
	print('------------------------------')
	try:
		print(type(error))
		tb.print_stack()
		t.sleep(2.5)
		tb.print_tb(error.__traceback__)
		print()
		print(str(type(error).__name__)+': '+str(error))
		print('------------------------------')
	except BaseException as e:
		print('Error catcher failed')
		print('------------------------------')
		if len(args) > 0 and args[0] > 3:
			print('Error catcher recursion detected, raising error')
			raise
		if len(args) == 0:
			print_error(e,1)
		else:
			print_error(e,args[0]+1)
	except:
		print('Error catcher failed with uncaught exception')