package com.michaelclerx.brute;

import java.util.Comparator;

/**
 * Represents a tested classifier option, for which statistics (mcc, auc, acc) are known.
 */
public class Solution implements Comparable<Solution>
{
	public final String option;
	public final double mcc;
	public final double auc;
	public final double acc;
	public final boolean useMcc;

	public Solution(String option, double mcc, double auc, double acc, boolean useMcc)
	{
		this.option = option;
		this.mcc = mcc;
		this.auc = auc;
		this.acc = acc;
		this.useMcc = useMcc;
	}

	public String toString()
	{
		if (useMcc) {
			return this.option + " MCC " + mcc;
		} else {
			return this.option + " AUC " + auc;
		}
	}
	
	@Override
	public int compareTo(Solution other)
	{
		double d1, d2;
		if (useMcc != other.useMcc) {
			throw new RuntimeException("Comparing MCC to AUC.");
		}
		if (useMcc) {
			d1 = mcc;
			d2 = other.mcc;
		} else {
			d1 = auc;
			d2 = other.auc;
		}
		
		// Return 1 if this is bigger than other
		// Use double compare (which handles -0 and 0 as well as NaN, but thinks NaN is
		// bigger than everything)
		// But make NaNs be smaller than everything
		boolean nan1 = Double.isNaN(d1);
		boolean nan2 = Double.isNaN(d2);
		if (nan1 && nan2) {
			return 0;
		} else if (nan1) {
			return -1;
		} else if (nan2) {
			return 1;
		}
		return Double.compare(d1, d2);
	}

	public static class DescendingComparator implements Comparator<Solution>
	{
		public int compare(Solution a, Solution b)
		{
			return b.compareTo(a);
		}
	}
	
}