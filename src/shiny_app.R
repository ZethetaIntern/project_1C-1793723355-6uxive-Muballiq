# Optional R Shiny prototype. Install shiny, readr, ggplot2 first.
library(shiny)
library(readr)
library(ggplot2)
signals <- read_csv("data/processed/FactSignals.csv", show_col_types=FALSE)
ui <- fluidPage(
  titlePanel("FX Signal Lab — R Shiny Prototype"),
  sidebarLayout(
    sidebarPanel(selectInput("pair","Currency pair",choices=unique(signals$PairName))),
    mainPanel(plotOutput("price"), tableOutput("latest"))
  )
)
server <- function(input, output) {
  filtered <- reactive(subset(signals, PairName == input$pair))
  output$price <- renderPlot({
    ggplot(filtered(), aes(x=as.POSIXct(DateTime), y=Close)) +
      geom_line() + labs(x="Time", y="Close", title="Historical FX close")
  })
  output$latest <- renderTable({
    tail(filtered()[,c("DateTime","Close","TA_Signal","ML_Signal","RL_Signal","Final_Signal","Confidence")], 10)
  })
}
shinyApp(ui, server)
