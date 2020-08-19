package com.michaelclerx.brute;

import java.util.ArrayList;
import java.util.StringJoiner;

/**
 * Quick class to make argument lists.
 */
public class Spec
{
	public final String classifier;
	public final ArrayList<String[]> options;

	public Spec(String classifier)
	{
		this.classifier = classifier;
		options = new ArrayList<String[]>();
	}

	public void add(Object... args)
	{
		String[] option = new String[args.length];
		int i = 0;
		for (Object arg : args) {
			option[i++] = arg.toString();
		}
		options.add(option);

	}

	public static String formatOption(String[] option)
	{
		StringJoiner joiner = new StringJoiner(" ");
		for (String arg : option) {
			joiner.add(arg);
		}
		return joiner.toString();
	}
}
