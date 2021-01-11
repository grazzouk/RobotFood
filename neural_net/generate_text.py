# Networks generatec using textgenrnn and built on Google Colabratory: https://minimaxir.com/2018/05/text-neural-networks/
import os
import argparse
from datetime import datetime

def parse_args(): 
	timestring = datetime.now().strftime('%Y%m%d_%H%M%S')
	default_output = 'output_{}.txt'.format(timestring)

	parser = argparse.ArgumentParser(description='Generate text for a model in a specific folder.')
	parser.add_argument('folder',
	                   help='the folder containing weights, vocab, and config')
	parser.add_argument('--max_gen', '-g', default=2000,
	                   help='the length of generation, default 2000')
	parser.add_argument('--temperature', '-t', default="1.0,0.5,0.2,0.2",
                   help='temperature sequence, default 1.0,0.5.0.2,0.2')
	parser.add_argument('--prefix', '-p', default=None,
                   help='the prefix, default none')
	parser.add_argument('--output', '-o', default=default_output,
               help='the output file, default output_[current time]')

	return parser.parse_args()

def generate_text():
	args = parse_args()
	# disables gpu with NN then imports textgenrnn (& tensorflow). use this if you do not want to setup your gpu
	#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
	from textgenrnn import textgenrnn

	timestring = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("{}: [generate_text.py] Recreating object...".format(timestring))

	textgen = textgenrnn(weights_path='{}/weights.hdf5'.format(args.folder),
	                       vocab_path='{}/vocab.json'.format(args.folder),
	                       config_path='{}/config.json'.format(args.folder))
	 

	# uncomment if you wish to also generate text to console
	# textgen.generate_samples(max_gen_length=1000)


	timestring = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("{}: [generate_text.py] Generating text...".format(timestring))
	temperature =  [float(temp) for temp in args.temperature.split(",")]
	prefix = args.prefix   # if you want each generated text to start with a given seed text
	n = 1
	max_gen_length = int(args.max_gen)

	textgen.generate_to_file(args.output,
	                         temperature=temperature,
	                         prefix=prefix,
	                         n=n,
	                         max_gen_length=max_gen_length)

	timestring = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print("{}: [generate_text.py] Text generation completed. Saved to: {}".format(timestring, args.output))
	
generate_text()
