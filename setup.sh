mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"jainadi5@msu.edu\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml