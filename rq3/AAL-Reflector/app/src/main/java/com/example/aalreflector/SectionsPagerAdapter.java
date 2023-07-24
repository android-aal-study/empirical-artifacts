package com.example.aalreflector;

import android.content.Context;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.annotation.StringRes;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;

/**
 * A [FragmentPagerAdapter] that returns a fragment corresponding to
 * one of the sections/tabs/pages.
 */
public class SectionsPagerAdapter extends FragmentPagerAdapter {
    private static final String TAG = "SectionsPagerAdapter";

    @StringRes
    private static final int[] TAB_TITLES = new int[]{
            R.string.tab_text_jar, R.string.tab_text_xml, R.string.tab_text_txt, R.string.tab_text_csv, R.string.tab_text_all
    };
    private final Context mContext;

    public SectionsPagerAdapter(Context context, FragmentManager fm) {
        super(fm);
        mContext = context;
    }

    @Override
    public Fragment getItem(int position) {
        Log.i(TAG, "getItem called position="+position);
        // getItem is called to instantiate the fragment for the given page.
        // Return a PlaceholderFragment (defined as a static inner class below).
        String aalType = mContext.getResources().getString(TAB_TITLES[position]);
        return PlaceholderFragment.newInstance(position, aalType);
    }

    @Nullable
    @Override
    public CharSequence getPageTitle(int position) {
        Log.i(TAG, "getPageTitle called position="+position);
        return mContext.getResources().getString(TAB_TITLES[position]);
    }

    @Override
    public int getCount() {
        return TAB_TITLES.length;
    }
}