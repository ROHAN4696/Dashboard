import streamlit as st
pages = [
   st.Page("./tab1.py", title="Tab 1", icon="📄"),
   st.Page("./tab2.py", title="Tab 2", icon="📊"),
   st.Page("./tab3.py", title="Tab 3", icon="📊"),
   st.Page("./tab4.py", title="Tab 4", icon="📊"),
   st.Page("./tab5.py", title="Tab 5", icon="📊"),
   st.Page("./tab6.py", title="Tab 6", icon="📊"),
   st.Page("./tab7.py", title="Tab 7", icon="📊"),
]

nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()