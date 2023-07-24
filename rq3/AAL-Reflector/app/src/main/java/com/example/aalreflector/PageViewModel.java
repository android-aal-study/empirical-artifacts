package com.example.aalreflector;

import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public class PageViewModel extends ViewModel {

    private String aalType;
    public void setAalType(String aalType) {
        this.aalType = aalType;
    }
    public String getAalType() {
        return aalType;
    }


    private MutableLiveData<Integer> mIndex = new MutableLiveData<>();
    public void setIndex(int index) {
        mIndex.setValue(index);
    }

}
