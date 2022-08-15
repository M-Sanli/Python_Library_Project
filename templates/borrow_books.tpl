
% rebase('templates/base.tpl', title="Library")
% include('templates/navigation_bar.tpl', page="borrow_book")
<div class="container">

    <div class="d-flex flex-row flex-wrap bd-highlight">
        % for book in books:
            % include("templates/book.tpl", book=book, card_type="to_borrow")
        % end
    </div>
</div>