cmake_minimum_required(VERSION 3.22)

project(Aria
    VERSION 0.0.1
    DESCRIPTION "AI-assisted DAW"
    LANGUAGES C CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
    add_compile_options(/utf-8)
endif()

add_subdirectory(External/JUCE)

juce_add_gui_app(Aria
    PRODUCT_NAME "Aria"
    COMPANY_NAME "Personal"
    BUNDLE_ID "com.personal.aria"
    VERSION "0.0.1"
)

juce_generate_juce_header(Aria)

target_sources(Aria PRIVATE
    src/Main.cpp
    src/MainComponent.cpp
    src/SineSynth.cpp
)

target_compile_definitions(Aria PRIVATE
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_APPLICATION_NAME_STRING="$<TARGET_PROPERTY:Aria,JUCE_PRODUCT_NAME>"
    JUCE_APPLICATION_VERSION_STRING="$<TARGET_PROPERTY:Aria,JUCE_VERSION>"
)

target_link_libraries(Aria PRIVATE
    juce::juce_audio_basics
    juce::juce_audio_devices
    juce::juce_audio_processors
    juce::juce_audio_utils
    juce::juce_core
    juce::juce_data_structures
    juce::juce_dsp
    juce::juce_events
    juce::juce_graphics
    juce::juce_gui_basics
    juce::juce_gui_extra
    PUBLIC
    juce::juce_recommended_config_flags
    juce::juce_recommended_lto_flags
    juce::juce_recommended_warning_flags
)
