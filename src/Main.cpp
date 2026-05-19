#include <JuceHeader.h>
#include "MainComponent.h"

class AriaApplication : public juce::JUCEApplication
{
public:
    AriaApplication() = default;

    const juce::String getApplicationName() override    { return ProjectInfo::projectName; }
    const juce::String getApplicationVersion() override { return ProjectInfo::versionString; }
    bool moreThanOneInstanceAllowed() override          { return false; }

    void initialise(const juce::String&) override
    {
        mainWindow = std::make_unique<MainWindow>(getApplicationName(), new MainComponent(), *this);
    }

    void shutdown() override
    {
        mainWindow = nullptr;
    }

    void systemRequestedQuit() override
    {
        quit();
    }

    void anotherInstanceStarted(const juce::String&) override {}

private:
    class MainWindow : public juce::DocumentWindow
    {
    public:
        MainWindow(juce::String name, juce::Component* c, JUCEApplication& a)
            : DocumentWindow(name,
                             juce::Desktop::getInstance().getDefaultLookAndFeel()
                                 .findColour(juce::ResizableWindow::backgroundColourId),
                             juce::DocumentWindow::allButtons),
              app(a)
        {
            setUsingNativeTitleBar(true);
            setContentOwned(c, true);
            setResizable(true, true);
            centreWithSize(900, 360);
            setVisible(true);
        }

        void closeButtonPressed() override
        {
            app.systemRequestedQuit();
        }

    private:
        JUCEApplication& app;
        JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(MainWindow)
    };

    std::unique_ptr<MainWindow> mainWindow;
};

START_JUCE_APPLICATION(AriaApplication)
