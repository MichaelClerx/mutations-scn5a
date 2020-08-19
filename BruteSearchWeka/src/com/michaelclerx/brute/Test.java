package com.michaelclerx.brute;

public class Test
{
	public final static boolean debug = false;

	public static void main(String[] args) throws Exception
	{
		String[] methods = { "zero-r", "random-forest", "naive-bayes", "mlp", "svm", "knn" };
		String[] datasets = { "changed", "act", "inact", "late", "zero" };
		
		//String[] datasets = {"dvi-disc"};

		Spec spec;
		Explorer exp;
		for (String data : datasets) {
			boolean mcc = data.equals("dvi-disc") ? false : true;			
			for (String method : methods) {
				spec = getBestSpec(method, data);
				exp = new Explorer(data  + ".arff",  spec, mcc);
				exp.test();
			}
		}
		System.out.println("Completely done!");
	}
		
	private static Spec getBestSpec(String method, String data)
	{
		if (method == "random-forest") {
			Spec spec = new Spec("weka.classifiers.trees.RandomForest");
			// Add default
			spec.add();
			// Add best
			if (data == "act") {
				spec.add("-P", 28, "-K", 3, "-I", 60);
			} else if (data == "inact") {
				spec.add("-P", 8, "-K", 6, "-I", 100, "-B");
			} else if (data == "late") {
				spec.add("-P", 96, "-K", 0, "-I", 50);
			} else if (data == "zero") {
				spec.add("-P", 88, "-K", 6, "-I", 40);
			} else if (data == "changed") {
				spec.add("-P", 12, "-K", 5, "-I", 20, "-B");
				spec.add("-P", 12, "-K", 0, "-I", 20, "-B");
				spec.add("-P", 16, "-K", 9, "-I", 20);
			} else if (data == "dvi-disc") {
				spec.add("-P", 84, "-K", 1, "-I", 20);
				spec.add("-P", 84, "-K", 1, "-I", 20, "-B");
			} else {
				System.err.println("Unknown data set.");
				System.exit(1);
			}	
			return spec;
		} else if (method == "naive-bayes") {
			Spec spec = new Spec("weka.classifiers.bayes.NaiveBayes");
			// Add default
			spec.add();
			// Add best
			if (data == "act") {
				// Default is best
			} else if (data == "inact") {
				spec.add("-K");
			} else if (data == "late") {
				spec.add("-D");
			} else if (data == "zero") {
				spec.add("-K");
			} else if (data == "changed") {
				spec.add("-D");
			} else if (data == "dvi-disc") {
				// Default is best
			} else {
				System.err.println("Unknown data set.");
				System.exit(1);
			}
			return spec;
		} else if (method == "mlp") {
			Spec spec = new Spec("weka.classifiers.functions.MLPClassifier");
			// Add default
			spec.add("-P", 1, "-E", 1, "-S", 1, "-L",
					"weka.classifiers.functions.loss.SquaredError", "-A",
					"weka.classifiers.functions.activation.ApproximateSigmoid");
			// Add best
			if (data == "act") {
				spec.add("-N", 3, "-R", 0.001, "-O", 1.0E-9, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else if (data == "inact") {
				spec.add("-N", 5, "-R", 1.0E-8, "-O", 1.0E-7, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else if (data == "late") {
				spec.add("-N", 3, "-R", 1.0E-7, "-O", 1.0E-5, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else if (data == "zero") {
				spec.add("-N", 7, "-R", 1.0E-6, "-O", 0.001, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else if (data == "changed") {
				spec.add("-N", 10, "-R", 1.0E-5, "-O", 1.0E-6, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
				spec.add("-N", 8, "-R", 1.0E-7, "-O", 1.0E-8, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else if (data == "dvi-disc") {
				spec.add("-N", 10, "-R", 0.01, "-O", 1.0E-8, "-P", 1, "-E", 1, "-S", 1, "-L",
						"weka.classifiers.functions.loss.SquaredError", "-A",
						"weka.classifiers.functions.activation.ApproximateSigmoid");
			} else {
				System.err.println("Unknown data set.");
				System.exit(1);
			}	
			return spec;
		} else if (method == "svm") {
			Spec spec = new Spec("weka.classifiers.functions.LibSVM");
			// Add default
			spec.add("-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			// Add best
			if (data == "act") {
				spec.add("-C", 4, "-G", 9.765625E-4, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else if (data == "inact") {
				spec.add("-C", 4, "-G", 9.765625E-4, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else if (data == "late") {
				spec.add("-C", 128, "-G", 4.8828125E-4, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else if (data == "zero") {
				spec.add("-C", 8, "-G", 3.0517578125E-5, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else if (data == "changed") {
				spec.add("-C", 512, "-G", 4.76837158203125E-7, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else if (data == "dvi-disc") {
				spec.add("-C", 1, "-G", 3.814697265625E-6, "-D", 3, "-seed", 1, "-W", 1, "-R", 0, "-M", 40);
			} else {
				System.err.println("Unknown data set.");
				System.exit(1);
			}
			return spec;
		} else if (method == "knn") {
			Spec spec = new Spec("weka.classifiers.lazy.IBk");
			// Add default
			spec.add();
			// Add best
			if (data == "act") {
				spec.add("-K", 6, "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.ChebyshevDistance");
			} else if (data == "inact") {
				spec.add("-K", 19, "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.ManhattanDistance");
			} else if (data == "changed") {
				spec.add("-K", 9, "-I", "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.ChebyshevDistance");
			} else if (data == "late") {
				spec.add("-K", 13, "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.ManhattanDistance");
			} else if (data == "zero") {
				spec.add("-K", 4, "-I", "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.EuclideanDistance");
			} else if (data == "dvi-disc") {
				spec.add("-K", 8, "-A", "weka.core.neighboursearch.LinearNNSearch -A weka.core.ChebyshevDistance");
			} else {
				System.err.println("Unknown data set.");
				System.exit(1);
			}
			return spec;
		} else if (method == "zero-r") {
			Spec spec = new Spec("weka.classifiers.rules.ZeroR");
			spec.add();
			return spec;
		} else {
			System.err.println("Unknown method.");
			System.exit(1);
		}
		return null;
	}
}