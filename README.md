# inventory-management- app

run it on local server
python manage.py runserver

urls and their use cases

{
    "get_list_of_all_boxes": {
        "url": "box-list/?length_more_than=5&volume_less_than=9",
        "authorization": "Logged-in",
        "filter_by": [
            "length_more_than",
            "length_less_than",
            "breadth_more_than",
            "breadth_less_than",
            "height_more_than",
            "height_less_than",
            "area_more_than",
            "area_less_than",
            "volume_more_than",
            "volume_less_than",
            "username",
            "before_date",
            "after_date"
        ]
    },
    "get_list_of_all_my_boxes": {
        "url": "myboxes/?length_more_than=5&volume_less_than=9",
        "authorization": "Logged-in",
        "filter_by": [
            "length_more_than",
            "length_less_than",
            "breadth_more_than",
            "breadth_less_than",
            "height_more_than",
            "height_less_than",
            "area_more_than",
            "area_less_than",
            "volume_more_than",
            "volume_less_than"
        ]
    },
    "add new box": {
        "url": "boxes/",
        "authorization": "Logged-in, Staff-User",
        "post request format": {
            "length": 1,
            "height": 5.33,
            "breadth": 6
        }
    },
    "update box": {
        "url": "boxes/id/",
        "authorization": "Logged-in, Staff-User",
        "put request format": {
            "length": 1,
            "breadth": 6
        }
    },
    "delete box": {
        "url": "myboxes/id/",
        "authorization": "Logged-in, Staff-User, box_creator_permission"
    }
}
